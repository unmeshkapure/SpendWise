import { Injectable, signal } from '@angular/core';

@Injectable({
    providedIn: 'root'
})
export class ThemeService {
    private readonly THEME_KEY = 'theme-preference';
    isDarkMode = signal<boolean>(true);

    constructor() {
        this.initializeTheme();
    }

    private initializeTheme() {
        const savedTheme = localStorage.getItem(this.THEME_KEY);
        if (savedTheme) {
            this.setTheme(savedTheme === 'dark');
        } else {
            // Default to dark mode
            this.setTheme(true);
        }
    }

    toggleTheme() {
        this.setTheme(!this.isDarkMode());
    }

    private setTheme(isDark: boolean) {
        this.isDarkMode.set(isDark);
        localStorage.setItem(this.THEME_KEY, isDark ? 'dark' : 'light');

        if (isDark) {
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
        }
    }
}
