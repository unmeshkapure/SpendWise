import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Goal {
    id?: number;
    title: string;
    target_amount: number;
    current_amount: number;
    target_date: string;
    is_completed?: boolean;
    is_locked?: boolean;
    description?: string;
}

@Injectable({
    providedIn: 'root'
})
export class GoalService {
    private apiUrl = '/api/v1/goals';

    constructor(private http: HttpClient) { }

    getGoals(): Observable<Goal[]> {
        return this.http.get<Goal[]>(`${this.apiUrl}/`);
    }

    createGoal(goal: Goal): Observable<Goal> {
        return this.http.post<Goal>(`${this.apiUrl}/`, goal);
    }

    updateGoal(id: number, goal: Partial<Goal>): Observable<Goal> {
        return this.http.put<Goal>(`${this.apiUrl}/${id}`, goal);
    }

    deleteGoal(id: number): Observable<any> {
        return this.http.delete(`${this.apiUrl}/${id}`);
    }

    addAmount(id: number, amount: number): Observable<Goal> {
        return this.http.post<Goal>(`${this.apiUrl}/${id}/add-amount?amount=${amount}`, {});
    }
}
