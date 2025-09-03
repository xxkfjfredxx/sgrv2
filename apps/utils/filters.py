def filter_by_active_company(queryset, user):
    if hasattr(user, "active_company") and user.active_company:
        return queryset.filter(company=user.active_company)
    return queryset.none()  # o queryset.all() si prefieres mostrar todo
