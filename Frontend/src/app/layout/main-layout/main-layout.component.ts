import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../auth/auth.service';

import { ThemeService } from '../../core/services/theme.service';

@Component({
    selector: 'app-main-layout',
    standalone: true,
    imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
    templateUrl: './main-layout.component.html',
    styleUrl: './main-layout.component.css'
})
export class MainLayoutComponent {
    constructor(
        public authService: AuthService,
        public themeService: ThemeService
    ) { }

    toggleTheme() {
        this.themeService.toggleTheme();
    }
}
