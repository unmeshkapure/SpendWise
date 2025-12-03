import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Forecast {
    month: number;
    year: number;
    predicted_budget: number;
    month_name: string;
}

@Injectable({
    providedIn: 'root'
})
export class PredictionService {
    private apiUrl = '/api/v1/predictions';

    constructor(private http: HttpClient) { }

    getBudgetPrediction(): Observable<number> {
        return this.http.get<number>(`${this.apiUrl}/budget`);
    }

    getForecast(monthsAhead: number = 3): Observable<Forecast[]> {
        return this.http.get<Forecast[]>(`${this.apiUrl}/forecast?months_ahead=${monthsAhead}`);
    }

    getTrends(monthsBack: number = 6): Observable<any> {
        return this.http.get<any>(`${this.apiUrl}/trends?months_back=${monthsBack}`);
    }
}
