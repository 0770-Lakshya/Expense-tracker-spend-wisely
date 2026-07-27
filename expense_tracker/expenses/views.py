import json
from datetime import datetime, date, timedelta
from urllib.parse import urlencode

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from .models import Expense, CATEGORY_CHOICES

VALID_CATEGORIES = {c[0] for c in CATEGORY_CHOICES}


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


def _validate_expense_data(title, amount_str, category, date_str):
    errors = {}
    if not title or not title.strip():
        errors['title'] = 'Title is required'
    if not amount_str:
        errors['amount'] = 'Amount is required'
    else:
        try:
            amount = float(amount_str)
            if amount <= 0:
                errors['amount'] = 'Amount must be positive'
        except (ValueError, TypeError):
            errors['amount'] = 'Invalid amount'
    if category not in VALID_CATEGORIES:
        errors['category'] = 'Invalid category'
    if date_str:
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            errors['date'] = 'Invalid date format'
    return errors


@login_required
def dashboard(request):
    """Main dashboard: add expense form + expense list."""
    today = date.today()
    start_date, end_date = _get_date_range(request)

    expenses = _get_filtered_expenses(request.user, start_date, end_date)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        amount_str = request.POST.get('amount', '').strip()
        category = request.POST.get('category', '')
        date_str = request.POST.get('date', '').strip()

        errors = _validate_expense_data(title, amount_str, category, date_str)

        if errors:
            context = {
                'expenses': expenses,
                'total': total,
                'categories': [c[0] for c in CATEGORY_CHOICES],
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'errors': errors,
                'form_data': request.POST,
            }
            return render(request, 'expenses/dashboard.html', context)

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount_str,
            category=category,
            date=date_str or today.isoformat(),
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

    today = date.today()
    last_month_end = today.replace(day=1) - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    last_30_days = today - timedelta(days=30)

    context = {
        'expenses': expenses,
        'total': total,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'today': today,
        'last_month_start': last_month_start.isoformat(),
        'last_month_end': last_month_end.isoformat(),
        'last_30_days': last_30_days,
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
    cat_counts = dict(
        expenses.values_list('category')
        .annotate(count=Count('id'))
    )
    category_summary = []
    for cat in category_data:
        category_summary.append({
            'category': cat['category'],
            'total': cat['total'],
            'count': cat_counts.get(cat['category'], 0),
            'percentage': round((cat['total'] / total * 100) if total > 0 else 0, 1)
        })

    monthly_data = list(
        Expense.objects.filter(user=request.user, date__gte=start_date, date__lte=end_date)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    for m in monthly_data:
        m['month_label'] = m['month'].strftime('%b %Y') if m['month'] else ''

    context = {
        'category_data': category_data,
        'category_data_json': json.dumps(category_data, cls=DjangoJSONEncoder),
        'category_summary': category_summary,
        'monthly_data': monthly_data,
        'total': total,
        'total_count': expenses.count(),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
    }
    return render(request, 'expenses/reports.html', context)


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == 'POST':
        expense.title = request.POST.get('title')
        expense.amount = request.POST.get('amount')
        expense.category = request.POST.get('category')
        expense.date = request.POST.get('date')
        expense.save()

        next_url = request.POST.get('next', '/')
        if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            next_url = '/'
        return redirect(next_url)
    return redirect('/')


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
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/'
    if params:
        next_url += '?' + urlencode(params)
    return redirect(next_url)