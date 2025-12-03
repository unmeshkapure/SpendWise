import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators, FormsModule } from '@angular/forms';
import { GoalService, Goal } from './goal.service';

@Component({
    selector: 'app-goals',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, FormsModule],
    templateUrl: './goals.component.html',
    styleUrl: './goals.component.css'
})
export class GoalsComponent implements OnInit {
    goals: Goal[] = [];
    goalForm: FormGroup;
    showForm: boolean = false;
    isLoading: boolean = false;

    constructor(
        private goalService: GoalService,
        private fb: FormBuilder
    ) {
        this.goalForm = this.fb.group({
            name: ['', Validators.required],
            target_amount: ['', [Validators.required, Validators.min(1)]],
            current_amount: [0, [Validators.required, Validators.min(0)]],
            deadline: ['', Validators.required]
        });
    }

    ngOnInit(): void {
        this.loadGoals();
    }

    loadGoals(): void {
        this.isLoading = true;
        this.goalService.getGoals().subscribe({
            next: (data) => {
                this.goals = data;
                this.isLoading = false;
            },
            error: (err) => {
                console.error('Error loading goals', err);
                this.isLoading = false;
            }
        });
    }

    toggleForm(): void {
        this.showForm = !this.showForm;
        if (!this.showForm) {
            this.goalForm.reset({ current_amount: 0 });
        }
    }

    onSubmit(): void {
        if (this.goalForm.valid) {
            this.isLoading = true;
            this.goalService.createGoal(this.goalForm.value).subscribe({
                next: (newGoal) => {
                    this.goals.push(newGoal);
                    this.toggleForm();
                    this.isLoading = false;
                },
                error: (err) => {
                    console.error('Error creating goal', err);
                    this.isLoading = false;
                }
            });
        }
    }

    deleteGoal(id: number | undefined): void {
        if (!id) return;
        if (confirm('Delete this goal?')) {
            this.goalService.deleteGoal(id).subscribe({
                next: () => {
                    this.goals = this.goals.filter(g => g.id !== id);
                },
                error: (err) => console.error(err)
            });
        }
    }

    getProgress(goal: Goal): number {
        if (!goal.target_amount) return 0;
        return Math.min(100, (goal.current_amount / goal.target_amount) * 100);
    }

    // Add Money Logic
    addingToGoalId: number | null = null;
    amountToAdd: number = 0;

    openAddAmount(goalId: number | undefined): void {
        if (!goalId) return;
        this.addingToGoalId = goalId;
        this.amountToAdd = 0;
    }

    cancelAddAmount(): void {
        this.addingToGoalId = null;
        this.amountToAdd = 0;
    }

    submitAddAmount(): void {
        if (this.addingToGoalId && this.amountToAdd > 0) {
            this.isLoading = true;
            this.goalService.addAmount(this.addingToGoalId, this.amountToAdd).subscribe({
                next: (updatedGoal) => {
                    // Update the goal in the list
                    const index = this.goals.findIndex(g => g.id === updatedGoal.id);
                    if (index !== -1) {
                        this.goals[index] = updatedGoal;
                    }
                    this.cancelAddAmount();
                    this.isLoading = false;
                },
                error: (err) => {
                    console.error('Error adding amount', err);
                    this.isLoading = false;
                }
            });
        }
    }
}
