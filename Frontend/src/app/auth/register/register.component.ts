import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../auth.service';

@Component({
    selector: 'app-register',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, RouterLink],
    templateUrl: './register.component.html',
    styleUrl: './register.component.css' // Reusing login styles or separate? Let's use separate but similar.
})
export class RegisterComponent {
    registerForm: FormGroup;
    error: string = '';
    isLoading: boolean = false;

    constructor(
        private fb: FormBuilder,
        private authService: AuthService,
        private router: Router
    ) {
        this.registerForm = this.fb.group({
            username: ['', [Validators.required, Validators.minLength(3)]],
            email: ['', [Validators.required, Validators.email]],
            full_name: ['', Validators.required],
            password: ['', [
                Validators.required,
                Validators.minLength(8),
                Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/)
            ]],
            confirmPassword: ['', Validators.required]
        }, { validator: this.passwordMatchValidator });
    }

    passwordMatchValidator(g: FormGroup) {
        return g.get('password')?.value === g.get('confirmPassword')?.value
            ? null : { mismatch: true };
    }

    onSubmit(): void {
        if (this.registerForm.valid) {
            this.isLoading = true;
            this.error = '';

            const { confirmPassword, ...userData } = this.registerForm.value;

            this.authService.register(userData).subscribe({
                next: () => {
                    // Auto login or redirect to login? Redirect to login for now.
                    this.router.navigate(['/auth/login']);
                },
                error: (err) => {
                    this.error = 'Registration failed. Username or email might be taken.';
                    this.isLoading = false;
                }
            });
        }
    }
}
