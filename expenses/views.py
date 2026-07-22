import json
from datetime import datetime, date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum
from django.utils import timezone
from .models import Expense, CATEGORY_CHOICES


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def _get_date_range(request):
    """Extract and validate date range from request."""
    today = date.today()
    start_date = request.GET.get('start_date', today.replace(day=1).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        start_date = today.replace(day=1)
    try:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        end_date = today

    return start_date, end_date


def _get_filtered_expenses(user, start_date, end_date):
    """Get expenses filtered by user and date range."""
    return Expense.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('-date')


def _get_category_data(expenses):
    """Get aggregated category data for charts."""
    return list(
        expenses.values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )


@login_required
def dashboard(request):
    """Main dashboard: add expense form + expense list."""
    today = date.today()
    start_date = request.GET.get('start_date', today.replace(day=1).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        start_date = today.replace(day=1)
    try:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        end_date = today

    expenses = _get_filtered_expenses(request.user, start_date, end_date)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        date_str = request.POST.get('date', today.isoformat())
        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            category=category,
            date=date_str,
        )
        return redirect(f'/?start_date={start_date}&end_date={end_date}')

    context = {
        'expenses': expenses,
        'total': total,
        'categories': [c[0] for c in CATEGORY_CHOICES],
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    }
    return render(request, 'expenses/dashboard.html', context)


@login_required
def filter_expenses(request):
    """Date filter page."""
    start_date, end_date = _get_date_range(request)
    expenses = _get_filtered_expenses(request.user, start_date, end_date)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'expenses': expenses,
        'total': total,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    }
    return render(request, 'expenses/filter.html', context)


@login_required
def reports(request):
    """Reports page with category pie chart."""
    start_date, end_date = _get_date_range(request)
    expenses = _get_filtered_expenses(request.user, start_date, end_date)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    category_data = _get_category_data(expenses)

    # Category summary for table
    category_summary = []
    for cat in category_data:
        cat_expenses = expenses.filter(category=cat['category'])
        category_summary.append({
            'category': cat['category'],
            'total': cat['total'],
            'count': cat_expenses.count(),
            'percentage': round((cat['total'] / total * 100) if total > 0 else 0, 1)
        })

    context = {
        'category_data': category_data,
        'category_data_json': json.dumps(category_data, cls=DjangoJSONEncoder),
        'category_summary': category_summary,
        'total': total,
        'total_count': expenses.count(),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    }
    return render(request, 'expenses/reports.html', context)


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    expense.delete()
    params = {}
    if start_date:
        params['start_date'] = start_date
    if end_date:
        params['end_date'] = end_date
    next_url = request.META.get('HTTP_REFERER', '/')
    if params:
        from urllib.parse import urlencode
        next_url += '?' + urlencode(params)
    return redirect(next_url)