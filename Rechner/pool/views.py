from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from .models import Topic, Person, Expense
from .forms import TopicForm, PersonForm, ExpenseForm


# Display and create new topics.
def topic_list(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_topic':
            topic_id = request.POST.get('topic_id')
            if topic_id:
                Topic.objects.filter(id=topic_id).delete()
            return redirect('topics_list')

        form = TopicForm(request.POST)
        if form.is_valid():
            # TODO Save the new topic to the database.
            form.save()

            return redirect('topics_list')
    else:
        form = TopicForm()

    # TODO Sort Objects by creation date
    
    topics = Topic.objects.all()
    return render(request, 'pool/themen_liste.html', {
        'topics': topics,
        'form': form,
    })


# Show the details of a topic.
def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)

    # Form handling (POST requests).
    if request.method == 'POST':
        action = request.POST.get('action')

        match action:
            case 'add_person':
                person_form = PersonForm(request.POST)
                if person_form.is_valid():
                    person = person_form.save(commit=False)
                    person.topic = topic
                    person.save()

            case 'add_expense':
                expense_form = ExpenseForm(request.POST, topic=topic)
                if expense_form.is_valid():
                    expense = expense_form.save(commit=False)
                    expense.topic = topic
                    expense.save()

            case 'delete_person':
                person_id = request.POST.get('person_id')
                if person_id:
                    Person.objects.filter(id=person_id, topic=topic).delete()

            case 'delete_expense':
                expense_id = request.POST.get('expense_id')
                if expense_id:
                    Expense.objects.filter(id=expense_id, topic=topic).delete()

        return redirect('topic_detail', topic_id=topic.id)

    # Initialize the browser interface (GET requests).
    person_form = PersonForm()
    expense_form = ExpenseForm(topic=topic)

    people = Person.objects.filter(topic=topic)
    expenses = Expense.objects.filter(topic=topic).select_related('person')

    total_expenses_amount = expenses.aggregate(Sum('amount'))['amount__sum']
    total_expenses = float(total_expenses_amount) if total_expenses_amount is not None else 0.0

    person_count = people.count()
    per_person_share = (total_expenses / person_count) if person_count > 0 else 0.0

    people_summary = []
    for person in people:
        person_expense_total = expenses.filter(person=person).aggregate(Sum('amount'))['amount__sum']
        spent_amount = float(person_expense_total) if person_expense_total is not None else 0.0
        balance = spent_amount - per_person_share

        people_summary.append({
            'id': person.id,
            'name': person.name,
            'spent_amount': spent_amount,
            'balance': balance,
        })

    settlement_list = []
    debtors = [item for item in people_summary if item['balance'] < -0.01]
    creditors = [item for item in people_summary if item['balance'] > 0.01]
    debtors.sort(key=lambda item: item['balance'])
    creditors.sort(key=lambda item: item['balance'], reverse=True)

    while debtors and creditors:
        debtor = debtors[0]
        creditor = creditors[0]
        amount = min(abs(debtor['balance']), creditor['balance'])

        if amount <= 0.01:
            break

        settlement_list.append({
            'from_person': debtor['name'],
            'to_person': creditor['name'],
            'amount': round(amount, 2),
        })

        debtor['balance'] = round(debtor['balance'] + amount, 2)
        creditor['balance'] = round(creditor['balance'] - amount, 2)

        if debtor['balance'] >= -0.01:
            debtors.pop(0)
        else:
            debtors[0] = debtor
            debtors.sort(key=lambda item: item['balance'])

        if creditor['balance'] <= 0.01:
            creditors.pop(0)
        else:
            creditors[0] = creditor
            creditors.sort(key=lambda item: item['balance'], reverse=True)

    return render(request, 'pool/thema_detail.html', {
        'topic': topic,
        'people': people,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'per_person_share': per_person_share,
        'person_form': person_form,
        'expense_form': expense_form,
        'people_summary': people_summary,
        'settlement_list': settlement_list,
    })


# Edit an existing expense.
def expense_edit(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    topic = expense.topic

    if request.method == 'POST':
        # Create an instance to update the existing value.
        form = ExpenseForm(request.POST, instance=expense, topic=topic)
        if form.is_valid():
            form.save()
            return redirect('topic_detail', topic_id=topic.id)
    else:
        form = ExpenseForm(instance=expense, topic=topic)

    return render(request, 'pool/ausgabe_bearbeiten.html', {
        'form': form,
        'expense': expense,
        'topic': topic,
    })