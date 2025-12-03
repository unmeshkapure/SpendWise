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
    summary = {
        totalBalance: 0,
        monthlyIncome: 0,
        monthlyExpense: 0,
        savingsRate: 0
    };

    recentTransactions: any[] = [];
    isLoading = true;

    constructor(private http: HttpClient) { }

    ngOnInit(): void {
        this.fetchDashboardData();
    }

    fetchDashboardData(): void {
        this.isLoading = true;
        this.http.get<any>('/api/v1/dashboard/summary').subscribe({
            next: (data) => {
                this.summary = {
                    totalBalance: data.summary.current_month_net, // Using net as balance for now
                    monthlyIncome: data.summary.current_month_income,
                    monthlyExpense: data.summary.current_month_expense,
                    savingsRate: data.summary.current_month_income > 0
                        ? Math.round(((data.summary.current_month_income - data.summary.current_month_expense) / data.summary.current_month_income) * 100)
                        : 0
                };
                this.recentTransactions = data.recent_transactions;
                this.isLoading = false;
            },
            error: (error) => {
                console.error('Error fetching dashboard data:', error);
                this.isLoading = false;
            }
        });
    }
}
