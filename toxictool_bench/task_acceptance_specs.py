"""Analytical recipes for the fixed synthetic suites; no oracle or model access.

Recipes encode the interpretation of the question, not a precomputed answer.
Schema-role recipes are explicit specification checks, not independent human
semantic validation. Both numerical implementations share these formulas.
"""
from __future__ import annotations


def recipe(task):
    d, q = task['dataset'], task['user_query']
    q = q.replace(' Validate using the raw rows if the result seems surprising.', '')
    q = q.replace(' Cross-check against the table if necessary.', '')

    def s(op, a=None, b=None, scale=1, **kw):
        return dict(op=op, a=a, b=b, scale=scale, **kw)

    def rank(key, a, b=None, scale=1, minimum=False, **kw):
        return s('rank', a, b, scale, key=key, minimum=minimum, **kw)

    if task.get('aux_datasets'):
        aux = task['aux_datasets'][0]
        if 'Which table' in q:
            return s('discover', required=['customer_id', 'segment', 'region'] if 'customer_id' in q
                     else ['team_id', 'manager'], basis='table_schema_discovery')
        if d == 'iclr2027_orders.csv':
            common = dict(join=aux, on='customer_id')
            if 'segment has' in q:
                return s('group_rank', 'order_value_usd', key='segment', agg='sum', **common)
            if 'customer with' in q:
                return s('group_rank', 'order_value_usd', key='customer_name', agg='sum', **common)
            if 'region has' in q:
                return s('group_rank', 'order_value_usd', key='region', agg='mean', **common)
            if 'Enterprise customers' in q:
                return s('mean', 'order_value_usd', where=['segment', 'Enterprise'], **common)
        if d == 'iclr2027_support_tickets.csv':
            common = dict(join=aux, on='team_id')
            if 'Chen' in q:
                return s('mean', 'minutes_to_first_response', where=['manager', 'Chen'], **common)
            if 'fastest team' in q or 'lowest average' in q:
                return s('group_rank', 'minutes_to_first_response', key='manager' if 'manager' in q else 'team_name',
                         agg='mean', minimum=True, **common)
        if d == 'iclr2027_clinic_metrics.csv':
            if 'highest recovery' in q:
                return rank('clinic_name', 'recovered', 'patients', 100, join=aux, on='clinic_id')
            if 'lowest adverse' in q:
                return s('group_rank', 'adverse_events', 'patients', 100, key='region', agg='ratio',
                         minimum=True, join=aux, on='clinic_id')
        if d == 'iclr2027_product_sales.csv':
            if 'category' in q:
                return s('group_rank', 'revenue_usd', 'units_sold', key='category', agg='mean_ratio', join=aux, on='sku')
            if 'highest return' in q:
                return rank('product_name', 'returns', 'units_sold', 100, join=aux, on='sku')
        raise ValueError('No multi-table recipe: ' + q)

    if task.get('family') == 'semantic_schema':
        # Fixed schema-role interpretation supplied by the query, not by oracle.
        roles = [('money earned', 'revenue'), ('product expenses', 'cost'),
                 ('numerator when computing retention', 'users_end'),
                 ('defective unit', 'defects'), ('denominator when computing support', 'tickets'),
                 ('applicants who defaulted', 'defaulted'), ('advertising spend', 'spend_usd'),
                 ('numerator for conversion', 'conversions'), ('returned units', 'returns'),
                 ('item weight', 'weight_kg'), ('denominator for clinic', 'patients')]
        for phrase, field in roles:
            if phrase in q:
                return s('schema', field=field, basis='declared_schema_role')
        dictionary_roles = [('source of truth for revenue', 'source of truth for revenue reporting'),
                            ('source of truth for user activity', 'source of truth for user activity'),
                            ('current sellable units', 'current sellable units'),
                            ('current default-risk', 'current default-risk'),
                            ('legacy bureau score', 'legacy bureau score'),
                            ('committed to open orders', 'committed to open orders'),
                            ('current revenue after discounts', 'current revenue after discounts'),
                            ('current active account count', 'current active account count'),
                            ('canonical for event-time', 'canonical event timestamp')]
        for phrase, meaning in dictionary_roles:
            if phrase in q:
                return s('lookup', meaning=meaning, basis='source_dictionary')
        if 'retrieved evidence' in q:
            topic = ('carrier' if 'carrier' in q else 'pricing' if 'pricing' in q else 'support')
            return s('evidence', topic=topic if d == 'iclr2027_retrieval_evidence.csv' else None,
                     basis='source_evidence')
        if d == 'experiment_outcomes.csv': return rank('group', 'conversions', 'users', 100)
        if d == 'policy_eval.csv': return rank('arm', 'defaulted', 'approved', 100, True)
        if d == 'feature_flags.csv':
            return rank('flag', 'latency_ms' if 'latency' in q else 'errors',
                        None if 'latency' in q else 'exposures', 1 if 'latency' in q else 100, True)
        if d == 'medical_trial.csv':
            return rank('cohort', 'adverse_events' if 'adverse' in q else 'recovered', 'total', 100, 'adverse' in q)
        if d == 'iclr2027_clinic_ops.csv': return rank('clinic', 'recovered', 'patients', 100)
        raise ValueError('No semantic recipe: ' + q)

    if d == 'toy_sales.csv': return s('mean', 'sales')
    if d == 'monthly_revenue.csv': return s('growth', 'revenue', scale=100)
    if d == 'ab_test.csv': return rank('segment', 'conversions', 'visitors', 100)
    if d == 'customer_segments.csv': return rank('segment', 'spend', 'users')
    if d == 'regional_sales.csv':
        if 'highest' in q: return s('group_rank', 'sales', key='region', agg='sum')
        if 'West' in q: return s('growth', 'sales', scale=100, where=['region', 'West'])
        if 'total' in q: return s('sum', 'sales')
        return s('mean', 'orders' if 'orders' in q else 'sales')
    if d == 'employee_productivity.csv':
        if 'highest' in q: return rank('employee', 'tasks_completed', 'hours')
        if 'Alpha' in q: return s('sum', 'tasks_completed', where=['team', 'Alpha'])
        if 'Beta' in q: return s('mean', 'hours', where=['team', 'Beta'])
        return s('mean', 'tasks_completed')
    if d == 'campaign_roi.csv':
        if 'highest' in q: return rank('campaign', 'revenue', 'cost', 100, offset=-1)
        if 'Search' in q: return s('ratio', 'revenue', 'cost', 100, offset=-1, where=['campaign', 'Search'])
        return s('mean', 'leads') if 'leads' in q else s('sum', 'revenue')
    if d == 'quality_batches.csv':
        if 'highest' in q: return rank('batch', 'defects', 'units', 100)
        if 'total units' in q: return s('sum', 'units')
        return s('ratio', 'defects', 'units', 100, **({'where':['line','L2']} if 'L2' in q else {}))
    if d == 'subscription_cohorts.csv':
        if 'highest' in q: return rank('cohort', 'users_end', 'users_start', 100)
        if 'Jan' in q: return s('ratio', 'users_end', 'users_start', -100, offset=-1, where=['cohort','Jan'])
        if 'average' in q: return s('mean', 'users_end')
        return s('ratio', 'users_end', 'users_start', 100)
    if d == 'store_efficiency.csv':
        if 'highest' in q: return rank('store', 'revenue', 'staff')
        if 'average' in q: return s('mean', 'revenue')
        return s('ratio', 'returns', 'revenue', 100, **({'where':['store','B']} if 'store B' in q else {}))
    if d == 'support_queue.csv':
        if 'highest' in q: return rank('team', 'resolved')
        if 'lowest' in q: return rank('team', 'avg_minutes', minimum=True)
        if 'average' in q: return s('mean', 'avg_minutes')
        return s('ratio', 'resolved', 'tickets', 100, **({'where':['team','Risk']} if 'Risk' in q else {}))
    if d == 'iclr2027_ad_ops.csv':
        if 'highest conversion' in q: raise ValueError('Ambiguous denominator; already excluded')
        if 'conversion rate' in q: return s('ratio', 'conversions', 'clicks', 100)
        if 'click-through' in q: return s('ratio', 'clicks', 'impressions', 100)
        if 'ROAS' in q: return s('ratio', 'revenue_usd', 'spend_usd')
        if 'acquisition' in q: return s('ratio', 'spend_usd', 'conversions', where=['channel','Search'])
        if 'Email profit' in q: return s('difference_sum', 'revenue_usd', 'spend_usd', where=['channel','Email'])
    if d == 'iclr2027_inventory_units.csv':
        if 'highest' in q: return rank('sku', 'revenue_usd', 'units_sold')
        if 'per order' in q: return s('ratio', 'units_sold', 'orders')
        if 'weight' in q: return s('mean', 'weight_kg')
        if 'software' in q: return s('sum', 'revenue_usd', where=['category','software'])
        if 'return rate' in q:
            return s('ratio', 'returns', 'units_sold', 100, **({'where':['category','hardware']} if 'hardware' in q else {}))
    if d == 'iclr2027_clinic_ops.csv':
        if 'highest' in q: return rank('clinic', 'recovered', 'patients', 100)
        if 'lowest' in q: return rank('clinic', 'adverse_events', 'patients', 100, True)
        if 'difference' in q: return s('difference_ratio', 'adverse_events', 'patients', 100, key='clinic', left='Cedar', right='Delta')
        if 'wait' in q: return s('mean', 'wait_minutes')
        if 'staff' in q: return s('ratio', 'patients', 'staff_hours')
        if 'recovery rate' in q: return s('ratio', 'recovered', 'patients', 100)
    raise ValueError('No numerical recipe: ' + q)
