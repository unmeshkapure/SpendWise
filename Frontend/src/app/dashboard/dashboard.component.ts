import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
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

    constructor(
        private http: HttpClient,
        private cdr: ChangeDetectorRef
    ) { }

    ngOnInit(): void {
        this.fetchDashboardData();
    }

    trends: any[] = [];

    fetchDashboardData(): void {
        this.isLoading = true;

        // Fetch Summary
        this.http.get<any>('/api/v1/dashboard/summary').subscribe({
            next: (data) => {
                this.summary = {
                    totalBalance: data.summary.current_month_net,
                    monthlyIncome: data.summary.current_month_income,
                    monthlyExpense: data.summary.current_month_expense,
                    savingsRate: data.summary.current_month_income > 0
                        ? Math.round(((data.summary.current_month_income - data.summary.current_month_expense) / data.summary.current_month_income) * 100)
                        : 0
                };
                this.recentTransactions = data.recent_transactions;
                this.checkLoading();
            },
            error: (error) => {
                console.error('Error fetching dashboard data:', error);
                this.checkLoading();
            }
        });

        // Fetch Trends
        this.http.get<any[]>('/api/v1/dashboard/trends').subscribe({
            next: (data) => {
                this.trends = data;
                this.checkLoading();
            },
            error: (error) => {
                console.error('Error fetching trends:', error);
                this.checkLoading();
            }
        });
    }

    private loadingCount = 0;
    private checkLoading() {
        this.loadingCount++;
        if (this.loadingCount >= 2) {
            this.isLoading = false;
            this.cdr.detectChanges();
            this.loadingCount = 0;
        }
    }
}
