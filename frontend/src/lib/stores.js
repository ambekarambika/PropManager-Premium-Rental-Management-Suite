import { writable } from 'svelte/store';

// Authentication Store
export const currentUser = writable(null);

// Navigation Store (current active view tab)
export const currentView = writable('dashboard');

// Search and Filter Store
export const globalSearch = writable('');

// Toast Alert Store
export const toast = writable(null);

export function showToast(message, type = 'info') {
  toast.set({ message, type });
  setTimeout(() => {
    toast.set(null);
  }, 4000);
}
