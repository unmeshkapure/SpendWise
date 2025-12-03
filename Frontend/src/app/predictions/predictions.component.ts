import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { PredictionService, Forecast } from './prediction.service';

@Component({
    selector: 'app-predictions',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './predictions.component.html',
    styleUrl: './predictions.component.css'
})
export class PredictionsComponent implements OnInit {
    forecasts: Forecast[] = [];
    nextMonthBudget: number = 0;
    isLoading: boolean = false;

    constructor(
        private predictionService: PredictionService,
        private cdr: ChangeDetectorRef
    ) { }

    ngOnInit(): void {
        this.loadPredictions();
    }

    loadPredictions(): void {
        this.isLoading = true;

        // Load forecast
        this.predictionService.getForecast(6).subscribe({
            next: (data) => {
                this.forecasts = data;
                if (data.length > 0) {
                    this.nextMonthBudget = data[0].predicted_budget;
                }
                this.isLoading = false;
                this.cdr.detectChanges();
            },
            error: (err) => {
                console.error('Error loading predictions', err);
                this.isLoading = false;
                this.cdr.detectChanges();
            }
        });
    }
}
