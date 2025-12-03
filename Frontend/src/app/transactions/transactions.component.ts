import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TransactionService, Transaction } from './transaction.service';

@Component({
    selector: 'app-transactions',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule],
    templateUrl: './transactions.component.html',
    styleUrl: './transactions.component.css'
})
export class TransactionsComponent implements OnInit {
    transactions: Transaction[] = [];
    transactionForm: FormGroup;
    showForm: boolean = false;
    isLoading: boolean = false;
    categories = ['Food', 'Transport', 'Utilities', 'Entertainment', 'Health', 'Salary', 'Investment', 'Other'];

    constructor(
        private transactionService: TransactionService,
        private fb: FormBuilder,
        private cdr: ChangeDetectorRef
    ) {
        this.transactionForm = this.fb.group({
            amount: ['', [Validators.required, Validators.min(0.01)]],
            category: ['', Validators.required],
            type: ['expense', Validators.required],
            description: ['', Validators.required],
            date: [new Date().toISOString().split('T')[0], Validators.required]
        });
    }

    ngOnInit(): void {
        this.loadTransactions();
    }

    loadTransactions(): void {
        this.isLoading = true;
        this.transactionService.getTransactions().subscribe({
            next: (data) => {
                this.transactions = data;
                this.isLoading = false;
                this.cdr.detectChanges();
            },
            error: (err) => {
                console.error('Error loading transactions', err);
                this.isLoading = false;
                this.cdr.detectChanges();
            }
        });
    }

    toggleForm(): void {
        this.showForm = !this.showForm;
        if (!this.showForm) {
            this.transactionForm.reset({
                type: 'expense',
                date: new Date().toISOString().split('T')[0]
            });
        }
    }

    onSubmit(): void {
        if (this.transactionForm.valid) {
            this.isLoading = true;
            const transactionData = this.transactionForm.value;

            this.transactionService.createTransaction(transactionData).subscribe({
                next: (newTransaction) => {
                    this.transactions.unshift(newTransaction);
                    this.toggleForm();
                    this.isLoading = false;
                },
                error: (err) => {
                    console.error('Error creating transaction', err);
                    this.isLoading = false;
                }
            });
        }
    }

    deleteTransaction(id: number | undefined): void {
        if (!id) return;

        if (confirm('Are you sure you want to delete this transaction?')) {
            this.transactionService.deleteTransaction(id).subscribe({
                next: () => {
                    this.transactions = this.transactions.filter(t => t.id !== id);
                },
                error: (err) => {
                    console.error('Error deleting transaction', err);
                }
            });
        }
    }
}
