from datetime import date


def get_fiscal_years_for_grant(start_date, end_date, fiscal_year_start_month=1):
    fiscal_years = []
    current_year = start_date.year
    while current_year <= end_date.year:
        fiscal_year_start = date(current_year, fiscal_year_start_month, 1)
        fiscal_year_end = fiscal_year_start.replace(
            month=fiscal_year_start.month + 11, day=31)
        if start_date <= fiscal_year_end and end_date >= fiscal_year_start:
            fiscal_years.append(current_year)
        current_year += 1
    return fiscal_years


def allocate_budget_for_grant(grant):
    fiscal_years = get_fiscal_years_for_grant(grant.start_date, grant.end_date)
    total_days = (grant.end_date - grant.start_date).days + 1
    allocations = {}

    for year in fiscal_years:
        fiscal_year_start = date(year, 1, 1)
        fiscal_year_end = date(year, 12, 31)

        overlap_start = max(grant.start_date, fiscal_year_start)
        overlap_end = min(grant.end_date, fiscal_year_end)
        overlap_days = (overlap_end - overlap_start).days + 1

        if overlap_days > 0:
            allocation = (overlap_days / total_days) * grant.amount
            allocations[year] = allocation

    return allocations
