from django.forms import DateTimeInput, CheckboxSelectMultiple


class BootstrapDateTimePickerInput(DateTimeInput):
    template_name = "widgets/bootstrap_datetimepicker.html"

    def get_context(self, name, value, attrs):
        datetimepicker_id = f"datetimepicker_{name}"
        if attrs is None:
            attrs = dict()
        attrs["data-target"] = f"#{datetimepicker_id}"
        attrs["class"] = "form-control datetimepicker-input"
        context = super().get_context(name, value, attrs)
        context["widget"]["datetimepicker_id"] = datetimepicker_id
        return context


class CheckboxSelectMultipleAsTable(CheckboxSelectMultiple):
    template_name = "widgets/checkbox_select_multiple_as_table.html"

    def get_context(self, name, value, attrs=None):
        # return {'widget': {
        #    'name': name,
        #    'value': value,
        # }}
        checkbox_id = f"checkbox_{name}"
        if attrs is None:
            attrs = dict()
        attrs["data-target"] = f"#{checkbox_id}"
        attrs["class"] = "form-control checkbox-input"
        context = super().get_context(name, value, attrs)
        context["widget"]["checkbox_id"] = checkbox_id
        return context

    # def render(self, name, value, attrs=None):
    #    context = self.get_context(name, value, attrs)
    #    template = loader.get_template(self.template_name).render(context)
    # return mark_safe(template)
    #    return "TEST"
