import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Transaction {
    id?: number;
    amount: number;
    category: string;
    type: 'income' | 'expense';
    description: string;
    date?: string;
}

@Injectable({
    providedIn: 'root'
})
export class TransactionService {
    private apiUrl = '/api/v1/transactions';

    constructor(private http: HttpClient) { }

    getTransactions(skip: number = 0, limit: number = 100): Observable<Transaction[]> {
        return this.http.get<Transaction[]>(`${this.apiUrl}/?skip=${skip}&limit=${limit}`);
    }

    createTransaction(transaction: Transaction): Observable<Transaction> {
        return this.http.post<Transaction>(`${this.apiUrl}/`, transaction);
    }

    deleteTransaction(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/${id}`);
    }
}
