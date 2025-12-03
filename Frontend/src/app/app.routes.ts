import { Routes } from '@angular/router';
import { LoginComponent } from './auth/login/login.component';
import { RegisterComponent } from './auth/register/register.component';
import { MainLayoutComponent } from './layout/main-layout/main-layout.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { TransactionsComponent } from './transactions/transactions.component';
import { PredictionsComponent } from './predictions/predictions.component';
import { GoalsComponent } from './goals/goals.component';
import { authGuard } from './auth/auth.guard';

export const routes: Routes = [
    { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
    {
        path: 'auth',
        children: [
            { path: 'login', component: LoginComponent },
            { path: 'register', component: RegisterComponent }
        ]
    },
    {
        path: '',
        component: MainLayoutComponent,
        canActivate: [authGuard],
        children: [
            { path: 'dashboard', component: DashboardComponent },
            { path: 'transactions', component: TransactionsComponent },
            { path: 'predictions', component: PredictionsComponent },
            { path: 'goals', component: GoalsComponent }
        ]
    },
    { path: '**', redirectTo: '/dashboard' }
];
