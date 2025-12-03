import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { jwtDecode } from 'jwt-decode';
import { Router } from '@angular/router';

export interface User {
    id: number;
    email: string;
    username: string;
    full_name: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
    user: User;
    username?: string;
}

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private apiUrl = '/api/v1/auth';
    private currentUserSubject = new BehaviorSubject<User | null>(null);
    public currentUser$ = this.currentUserSubject.asObservable();

    constructor(private http: HttpClient, private router: Router) {
        this.loadUserFromToken();
    }

    private loadUserFromToken(): void {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const decoded: any = jwtDecode(token);
                if (decoded.exp * 1000 < Date.now()) {
                    this.logout();
                    return;
                }

                // Fetch full user profile to ensure we have the username
                this.http.get<User>(`${this.apiUrl}/me`).subscribe({
                    next: (user) => {
                        this.currentUserSubject.next(user);
                    },
                    error: () => {
                        // Fallback to token data if API fails
                        this.currentUserSubject.next({ username: decoded.username || decoded.sub } as User);
                    }
                });
            } catch (error) {
                this.logout();
            }
        }
    }

    login(credentials: any): Observable<AuthResponse> {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        return this.http.post<AuthResponse>(`${this.apiUrl}/login`, formData).pipe(
            tap(response => {
                localStorage.setItem('access_token', response.access_token);
                // The backend returns access_token and token_type. 
                // We might need to fetch the user details separately or decode the token.
                // Let's decode for now.
                const decoded: any = jwtDecode(response.access_token);
                this.currentUserSubject.next({ username: decoded.username || response.username } as User);
            })
        );
    }

    register(userData: any): Observable<User> {
        return this.http.post<User>(`${this.apiUrl}/register`, userData);
    }

    logout(): void {
        localStorage.removeItem('access_token');
        this.currentUserSubject.next(null);
        this.router.navigate(['/auth/login']);
    }

    isAuthenticated(): boolean {
        return !!this.currentUserSubject.value;
    }

    getToken(): string | null {
        return localStorage.getItem('access_token');
    }
}
