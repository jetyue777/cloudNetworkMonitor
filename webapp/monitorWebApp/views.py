from django.shortcuts import render, render_to_response


# Create your views here.
def main (request):
    return render_to_response('main.html')