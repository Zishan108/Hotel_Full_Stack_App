// static/js/storage.js
class HotelStorageManager {
    constructor() {
        this.cookieExpiryDays = 30;
        this.storageKeys = {
            PREFERRED_HOTEL: 'preferred_hotel_slug',
            RECENT_HOTELS: 'recent_hotels',
            LANGUAGE: 'language_preference',
            THEME: 'theme_preference',
            NEWSLETTER_SUBSCRIBED: 'newsletter_subscribed',
            BOOKING_FORM_DATA: 'booking_form_data',
            COMPARISON_LIST: 'hotel_comparison_list',
            LAST_VISIT: 'last_visit_date'
        };
    }

    // ========== COOKIE METHODS ==========
    setCookie(name, value, days = this.cookieExpiryDays) {
        const date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        const expires = "expires=" + date.toUTCString();
        document.cookie = `${name}=${encodeURIComponent(value)}; ${expires}; path=/; SameSite=Lax`;
    }

    getCookie(name) {
        const nameEQ = name + "=";
        const ca = document.cookie.split(';');
        for(let i = 0; i < ca.length; i++) {
            let c = ca[i];
            while (c.charAt(0) === ' ') {
                c = c.substring(1);
            }
            if (c.indexOf(nameEQ) === 0) {
                return decodeURIComponent(c.substring(nameEQ.length, c.length));
            }
        }
        return null;
    }

    deleteCookie(name) {
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
    }

    // ========== LOCALSTORAGE METHODS ==========
    setLocal(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Error saving to localStorage:', e);
            return false;
        }
    }

    getLocal(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    }

    removeLocal(key) {
        localStorage.removeItem(key);
    }

    clearLocal() {
        localStorage.clear();
    }

    // ========== SPECIFIC HOTEL-RELATED METHODS ==========
    savePreferredHotel(hotelSlug) {
        // Save to cookie for server-side access
        this.setCookie(this.storageKeys.PREFERRED_HOTEL, hotelSlug);
        
        // Save to localStorage for client-side access
        const recentHotels = this.getRecentHotels();
        if (!recentHotels.includes(hotelSlug)) {
            recentHotels.unshift(hotelSlug);
            // Keep only last 5 hotels
            if (recentHotels.length > 5) {
                recentHotels.pop();
            }
            this.setLocal(this.storageKeys.RECENT_HOTELS, recentHotels);
        }
    }

    getPreferredHotel() {
        return this.getCookie(this.storageKeys.PREFERRED_HOTEL);
    }

    getRecentHotels() {
        return this.getLocal(this.storageKeys.RECENT_HOTELS, []);
    }

    addToComparison(hotelSlug, hotelName) {
        const comparisonList = this.getLocal(this.storageKeys.COMPARISON_LIST, []);
        
        // Check if hotel already in list
        if (!comparisonList.some(hotel => hotel.slug === hotelSlug)) {
            comparisonList.push({
                slug: hotelSlug,
                name: hotelName,
                addedAt: new Date().toISOString()
            });
            
            // Keep only last 3 hotels for comparison
            if (comparisonList.length > 3) {
                comparisonList.shift();
            }
            
            this.setLocal(this.storageKeys.COMPARISON_LIST, comparisonList);
            return true;
        }
        return false;
    }

    getComparisonList() {
        return this.getLocal(this.storageKeys.COMPARISON_LIST, []);
    }

    removeFromComparison(hotelSlug) {
        const comparisonList = this.getComparisonList();
        const newList = comparisonList.filter(hotel => hotel.slug !== hotelSlug);
        this.setLocal(this.storageKeys.COMPARISON_LIST, newList);
        return newList;
    }

    saveBookingFormData(formData) {
        this.setLocal(this.storageKeys.BOOKING_FORM_DATA, {
            ...formData,
            savedAt: new Date().toISOString()
        });
    }

    getBookingFormData() {
        const data = this.getLocal(this.storageKeys.BOOKING_FORM_DATA);
        // Clear after 24 hours
        if (data && data.savedAt) {
            const savedTime = new Date(data.savedAt).getTime();
            const now = new Date().getTime();
            if (now - savedTime > 24 * 60 * 60 * 1000) {
                this.removeLocal(this.storageKeys.BOOKING_FORM_DATA);
                return null;
            }
        }
        return data;
    }

    clearBookingFormData() {
        this.removeLocal(this.storageKeys.BOOKING_FORM_DATA);
    }

    setNewsletterSubscription(email, subscribed = true) {
        this.setLocal(this.storageKeys.NEWSLETTER_SUBSCRIBED, {
            email: email,
            subscribed: subscribed,
            subscribedAt: new Date().toISOString()
        });
        
        // Also set cookie for server-side tracking
        this.setCookie('newsletter_subscribed', 'true', 365);
    }

    isNewsletterSubscribed() {
        return this.getLocal(this.storageKeys.NEWSLETTER_SUBSCRIBED, false);
    }

    setThemePreference(theme) {
        this.setLocal(this.storageKeys.THEME, theme);
        document.documentElement.setAttribute('data-theme', theme);
    }

    getThemePreference() {
        return this.getLocal(this.storageKeys.THEME, 'light');
    }

    setLanguagePreference(lang) {
        this.setCookie(this.storageKeys.LANGUAGE, lang);
        this.setLocal(this.storageKeys.LANGUAGE, lang);
    }

    getLanguagePreference() {
        return this.getLocal(this.storageKeys.LANGUAGE) || 
               this.getCookie(this.storageKeys.LANGUAGE) || 
               'en';
    }

    // ========== ANALYTICS & TRACKING ==========
    trackVisit() {
        const lastVisit = this.getLocal(this.storageKeys.LAST_VISIT);
        const currentVisit = new Date().toISOString();
        
        // Set cookie for first visit detection
        if (!this.getCookie('first_visit')) {
            this.setCookie('first_visit', currentVisit, 365);
        }
        
        // Update last visit
        this.setLocal(this.storageKeys.LAST_VISIT, currentVisit);
        this.setCookie('last_visit', currentVisit, 30);
        
        return {
            firstVisit: this.getCookie('first_visit'),
            lastVisit: lastVisit,
            currentVisit: currentVisit
        };
    }

    // ========== CONSENT MANAGEMENT ==========
    setConsent(consentType, granted) {
        this.setCookie(`consent_${consentType}`, granted ? 'true' : 'false', 365);
        this.setLocal(`consent_${consentType}`, granted);
    }

    getConsent(consentType) {
        const cookieValue = this.getCookie(`consent_${consentType}`);
        return cookieValue === 'true';
    }

    // ========== UTILITY METHODS ==========
    isStorageAvailable() {
        try {
            const testKey = '__storage_test__';
            localStorage.setItem(testKey, testKey);
            localStorage.removeItem(testKey);
            return true;
        } catch (e) {
            return false;
        }
    }

    clearAllHotelData() {
        // Clear only hotel-related data
        this.removeLocal(this.storageKeys.RECENT_HOTELS);
        this.removeLocal(this.storageKeys.COMPARISON_LIST);
        this.removeLocal(this.storageKeys.BOOKING_FORM_DATA);
        this.deleteCookie(this.storageKeys.PREFERRED_HOTEL);
    }
}

// Create global instance
const hotelStorage = new HotelStorageManager();