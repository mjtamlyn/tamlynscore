from django.shortcuts import redirect


def input_arrows_archer(request, **kwargs):
    return redirect('score_sheet', permanent=True, **kwargs)
