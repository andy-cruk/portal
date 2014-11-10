from bootstrap3.renderers import FieldRenderer


class PortalRenderer(FieldRenderer):
    """
    Field renderer for django-bootstrap3 form rendered that ensure addon_before and _after can be passed in the attrs
    of the field widget
    """
    def __init__(self, field, *args, **kwargs):
        super(PortalRenderer, self).__init__(field, *args, **kwargs)
        self.addon_before = self.initial_attrs.get('addon_before', '')
        self.addon_after = self.initial_attrs.get('addon_after', '')