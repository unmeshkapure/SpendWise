import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
    selector: 'app-dashboard',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './dashboard.component.html',
    styleUrl: './dashboard.component.css'
})
export class DashboardComponent implements OnInit {
    // Mock data for now, will replace with API calls
    summary = {
        totalBalance: 12500.50,
        monthlyIncome: 4500.00,
        monthlyExpense: 2300.25,
        savingsRate: 48
    };

    recentTransactions = [
        { id: 1, description: 'Grocery Store', amount: -150.00, date: new Date(), category: 'Food', type: 'expense' },
        { id: 2, description: 'Salary Deposit', amount: 4500.00, date: new Date(), category: 'Income', type: 'income' },
        { id: 3, description: 'Netflix Subscription', amount: -15.99, date: new Date(), category: 'Entertainment', type: 'expense' },
        { id: 4, description: 'Electric Bill', amount: -120.50, date: new Date(), category: 'Utilities', type: 'expense' }
    ];

    constructor(private http: HttpClient) { }

    ngOnInit(): void {
        // this.fetchDashboardData();
    }

    fetchDashboardData(): void {
        // this.http.get('/api/v1/dashboard/summary').subscribe(...)
    }
}
