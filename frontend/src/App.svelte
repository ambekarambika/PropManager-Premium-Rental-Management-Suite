<script>
  import { onMount } from 'svelte';
  import { currentUser, currentView, globalSearch, toast, showToast } from './lib/stores.js';
  import * as api from './lib/api.js';

  // Import views
  import LandingPage from './components/LandingPage.svelte';
  import Dashboard from './components/Dashboard.svelte';
  import Properties from './components/Properties.svelte';
  import Tenants from './components/Tenants.svelte';
  import Agreements from './components/Agreements.svelte';
  import Payments from './components/Payments.svelte';
  import Maintenance from './components/Maintenance.svelte';
  import Users from './components/Users.svelte';
  import Settings from './components/Settings.svelte';

  let initialized = false;
  let showLoginOverlay = false;
  let showRegisterForm = false;
  
  // Auth Form variables
  let loginEmail = 'rajesh@example.com';
  let loginPassword = 'password';
  let registerName = '';
  let registerEmail = '';
  let registerPassword = '';
  let registerRole = 'tenant';

  // Active details modal variable passed to Properties view
  let activePropertyId = null;

  onMount(async () => {
    await checkSession();
    initialized = true;
  });

  async function checkSession() {
    try {
      const user = await api.getCurrentUser();
      currentUser.set(user);
      if (user) {
        currentView.set('dashboard');
      } else {
        currentView.set('landing');
      }
    } catch (e) {
      console.error(e);
      currentUser.set(null);
      currentView.set('landing');
    }
  }

  async function handleLoginSubmit(e) {
    e.preventDefault();
    try {
      const data = await api.login(loginEmail, loginPassword);
      currentUser.set(data.user);
      currentView.set('dashboard');
      showLoginOverlay = false;
      showToast(`Welcome back, ${data.user.name}!`, 'success');
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function handleRegisterSubmit(e) {
    e.preventDefault();
    try {
      await api.register(registerName, registerEmail, registerPassword, registerRole);
      showToast('Account registered successfully! Please log in.', 'success');
      showRegisterForm = false;
      loginEmail = registerEmail;
      loginPassword = registerPassword;
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function handleLogout() {
    api.logout();
    currentUser.set(null);
    currentView.set('landing');
    showToast('Logged out successfully', 'info');
  }

  function switchView(viewName) {
    currentView.set(viewName);
    globalSearch.set(''); // reset search
  }

  function handleQuickRoleSelect(email) {
    loginEmail = email;
    loginPassword = 'password';
  }

  function handleViewDetailsFromLanding(event) {
    activePropertyId = event.detail.propertyId;
    currentView.set('properties');
  }

  // Capitalize view title
  $: viewTitle = $currentView === 'dashboard' ? 'Overview Dashboard' : 
                 $currentView === 'payments' ? 'Rent Ledger' :
                 $currentView === 'properties' ? 'Properties Portfolio' :
                 $currentView.charAt(0).toUpperCase() + $currentView.slice(1);

  $: initials = $currentUser ? $currentUser.name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() : '';
</script>

{#if !initialized}
  <div style="height:100vh; display:flex; align-items:center; justify-content:center; background:var(--bg-tertiary); color:var(--text-secondary); font-family:var(--font-sans)">
    <div style="text-align:center;">
      <i class="ti ti-loader animate-spin" style="font-size:32px; color:var(--primary);"></i>
      <div style="margin-top:10px; font-weight:600;">Loading PropManager Suite...</div>
    </div>
  </div>
{:else}
  <!-- Global Toast -->
  {#if $toast}
    <div class="toast active toast-{$toast.type}">
      <i class="ti {$toast.type === 'success' ? 'ti-circle-check' : $toast.type === 'error' ? 'ti-alert-circle' : 'ti-info-circle'}"></i>
      <span id="toast-message">{$toast.message}</span>
    </div>
  {/if}

  {#if $currentView === 'landing'}
    <LandingPage 
      on:login-click={() => { showLoginOverlay = true; showRegisterForm = false; }} 
      on:view-details={handleViewDetailsFromLanding}
    />
  {:else}
    <!-- Main Dashboard Application layout -->
    <div class="prm-root">
      <!-- Sidebar Navigation -->
      <aside class="sidebar">
        <div class="sidebar-logo">
          <div class="logo-mark" on:click={() => switchView('dashboard')} style="cursor: pointer;">
            <div class="logo-icon"><i class="ti ti-building"></i></div>
            <div>
              <div class="logo-text">PropManager</div>
              <div class="logo-sub">Rental Suite</div>
            </div>
          </div>
        </div>

        <nav class="nav-section">
          <div class="nav-label">Overview</div>
          <div class="nav-item {$currentView === 'dashboard' ? 'active' : ''}" on:click={() => switchView('dashboard')}>
            <i class="ti ti-layout-dashboard"></i> Dashboard
          </div>
          <div class="nav-item {$currentView === 'properties' ? 'active' : ''}" on:click={() => switchView('properties')}>
            <i class="ti ti-building-estate"></i> Properties
          </div>
          {#if $currentUser.role !== 'tenant'}
            <div class="nav-item {$currentView === 'tenants' ? 'active' : ''}" on:click={() => switchView('tenants')}>
              <i class="ti ti-users"></i> Tenants
            </div>
          {/if}
          <div class="nav-item {$currentView === 'maintenance' ? 'active' : ''}" on:click={() => switchView('maintenance')}>
            <i class="ti ti-tool"></i> Maintenance
          </div>
          {#if $currentUser.role === 'admin'}
            <div class="nav-item {$currentView === 'users' ? 'active' : ''}" on:click={() => switchView('users')}>
              <i class="ti ti-user-cog"></i> Users
            </div>
          {/if}

          <div class="nav-label">Finance</div>
          <div class="nav-item {$currentView === 'payments' ? 'active' : ''}" on:click={() => switchView('payments')}>
            <i class="ti ti-receipt"></i> Rent Ledger
          </div>
          <div class="nav-item {$currentView === 'agreements' ? 'active' : ''}" on:click={() => switchView('agreements')}>
            <i class="ti ti-file-text"></i> Agreements
          </div>

          <div class="nav-label">Settings</div>
          <div class="nav-item {$currentView === 'settings' ? 'active' : ''}" on:click={() => switchView('settings')}>
            <i class="ti ti-settings"></i> Profile
          </div>
        </nav>

        <div class="sidebar-bottom">
          <div class="user-chip" on:click={handleLogout} title="Click to logout">
            <div class="avatar">{initials}</div>
            <div class="user-info">
              <div class="user-name">{$currentUser.name}</div>
              <div class="user-role">{$currentUser.role === 'manager' ? 'Property Manager' : $currentUser.role}</div>
            </div>
            <div style="font-size: 16px; color: var(--text-tertiary);"><i class="ti ti-logout"></i></div>
          </div>
        </div>
      </aside>

      <!-- Main Panel -->
      <main class="main">
        <header class="topbar">
          <div class="topbar-title">{viewTitle}</div>
          
          {#if $currentView === 'properties'}
            <div class="search-box">
              <i class="ti ti-search"></i>
              <input type="text" bind:value={$globalSearch} placeholder="Search properties...">
            </div>
          {/if}
        </header>

        <div class="content">
          {#if $currentView === 'dashboard'}
            <Dashboard user={$currentUser} on:view-details={handleViewDetailsFromLanding} />
          {:else if $currentView === 'properties'}
            <Properties user={$currentUser} bind:activePropertyId />
          {:else if $currentView === 'tenants'}
            <Tenants user={$currentUser} />
          {:else if $currentView === 'agreements'}
            <Agreements user={$currentUser} />
          {:else if $currentView === 'payments'}
            <Payments user={$currentUser} />
          {:else if $currentView === 'maintenance'}
            <Maintenance user={$currentUser} />
          {:else if $currentView === 'users'}
            <Users />
          {:else if $currentView === 'settings'}
            <Settings />
          {/if}
        </div>
      </main>
    </div>
  {/if}
{/if}

<!-- =========================
     AUTH DIALOG OVERLAY (LOGIN / REGISTER)
     ========================= -->
{#if showLoginOverlay}
  <div class="auth-container" id="auth-overlay">
    <div class="auth-card" style="position: relative;">
      <button type="button" class="close-auth-btn" on:click={() => showLoginOverlay = false} style="position: absolute; top: 15px; right: 15px; background: transparent; border: none; font-size: 20px; color: var(--text-secondary); cursor: pointer;"><i class="ti ti-x"></i></button>
      <div class="auth-header">
        <div class="auth-logo"><i class="ti ti-building"></i></div>
        <h1 class="auth-title">PropManager</h1>
        <p class="auth-subtitle">Rental Suite System Login</p>
      </div>

      {#if !showRegisterForm}
        <!-- Mock Mode Quick Role Selector -->
        <div class="role-select-box">
          <div class="role-select-title">Quick Role Selector (Mock Mode)</div>
          <div class="role-btn-group">
            <button type="button" class="role-btn {loginEmail === 'rajesh@example.com' ? 'active' : ''}" on:click={() => handleQuickRoleSelect('rajesh@example.com')}>Manager</button>
            <button type="button" class="role-btn {loginEmail === 'admin@example.com' ? 'active' : ''}" on:click={() => handleQuickRoleSelect('admin@example.com')}>Admin</button>
            <button type="button" class="role-btn {loginEmail === 'arjun@example.com' ? 'active' : ''}" on:click={() => handleQuickRoleSelect('arjun@example.com')}>Tenant</button>
          </div>
        </div>

        <form on:submit={handleLoginSubmit}>
          <div class="form-group">
            <label class="form-label" for="login-email">Email Address</label>
            <input type="email" id="login-email" bind:value={loginEmail} class="form-control" placeholder="enter email..." required>
          </div>
          <div class="form-group">
            <label class="form-label" for="login-password">Password</label>
            <input type="password" id="login-password" bind:value={loginPassword} class="form-control" placeholder="••••••••" required>
          </div>
          <button type="submit" class="topbar-btn primary" style="width: 100%; justify-content: center; padding: 12px; margin-top: 10px;">Sign In</button>
          <p style="font-size: 12px; text-align: center; margin-top: 16px; color: var(--text-secondary);">
            Don't have an account? <span on:click={() => showRegisterForm = true} style="color: var(--primary); font-weight: 600; text-decoration: none; cursor: pointer;">Register here</span>
          </p>
        </form>
      {:else}
        <form on:submit={handleRegisterSubmit}>
          <div class="form-group">
            <label class="form-label" for="register-name">Full Name</label>
            <input type="text" id="register-name" bind:value={registerName} class="form-control" placeholder="e.g. Rajesh Kumar" required>
          </div>
          <div class="form-group">
            <label class="form-label" for="register-email">Email Address</label>
            <input type="email" id="register-email" bind:value={registerEmail} class="form-control" placeholder="name@example.com" required>
          </div>
          <div class="form-group">
            <label class="form-label" for="register-password">Password</label>
            <input type="password" id="register-password" bind:value={registerPassword} class="form-control" placeholder="Minimum 6 characters" required>
          </div>
          <div class="form-group">
            <label class="form-label" for="register-role">Register As</label>
            <select id="register-role" bind:value={registerRole} class="form-control" required>
              <option value="tenant">Tenant</option>
              <option value="manager">Property Manager</option>
            </select>
          </div>
          <button type="submit" class="topbar-btn primary" style="width: 100%; justify-content: center; padding: 12px; margin-top: 10px;">Create Account</button>
          <p style="font-size: 12px; text-align: center; margin-top: 16px; color: var(--text-secondary);">
            Already have an account? <span on:click={() => showRegisterForm = false} style="color: var(--primary); font-weight: 600; text-decoration: none; cursor: pointer;">Login here</span>
          </p>
        </form>
      {/if}
    </div>
  </div>
{/if}

<style>
  /* Local animations spin */
  .animate-spin {
    animation: spin 1s linear infinite;
    display: inline-block;
  }
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
