from django import template 
from django.core.cache import cache 

register =template.Library ()

@register.inclusion_tag("includes/sidebar_dynamic.html",takes_context=True )
def render_sidebar(context ):
    popular_tags =cache.get("sidebar_popular_tags",[])
    best_users =cache.get("sidebar_best_users",[])
    return {"popular_tags":popular_tags,"best_users":best_users}
