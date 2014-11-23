from django.core.context_processors import csrf, request
from django.forms.formsets import BaseFormSet, formset_factory
from django.shortcuts import render, render_to_response

from monitorWebApp.configure_form import configure_form


# Create your views here.
def main (request):
    return render_to_response('main.html')

def test (request):
    return render_to_response('index.html')

def configure (request):
    # This class is used to make empty formset forms required
    class RequiredFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            super(RequiredFormSet, self).__init__(*args, **kwargs)
            for form in self.forms:
                form.empty_permitted = False

    configureFormSet = formset_factory(configure_form, formset=RequiredFormSet)
    
    if request.method == 'POST': # If the form has been submitted...
        
        # Create a formset from the submitted data
        configure_formset_raw = configureFormSet(request.POST, request.FILES)
        print "==================================="
        print configure_formset_raw
        
        if configure_formset_raw.is_valid():
            
            external_ips = []
            user_names = []
            
            for form in configure_formset_raw.forms:
                config_form = form.cleaned_data
                external_ip = config_form.get('external_ip')
                user_name = config_form.get('user_name')
                #print "+++++++++++++++++++++++++++++++++++++++"
                #print external_ip
                #print user_name
                external_ips.append(external_ip)
                user_names.append(user_name)
            
            print "000000000000000"
            print external_ips
            print user_names

            request.session["external_ips"] = external_ips
            request.session["user_names"] = user_names
            
            args_done = {}
            args_done.update(csrf(request))
        
            args_done['external_ips'] = external_ips
            args_done['user_names'] = user_names
            return render_to_response('configure_done.html', args_done)
    else:
        configure_formset_raw = configureFormSet()
    
    args = {'configure_formset_raw': configure_formset_raw,}
    args.update(csrf(request))
    
    return render_to_response('configure.html', args)

