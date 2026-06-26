<script>
  import { onMount } from 'svelte';
  import * as api from '../lib/api.js';
  import { showToast } from '../lib/stores.js';

  let users = [];
  let loading = true;

  onMount(async () => {
    await loadUsers();
  });

  async function loadUsers() {
    try {
      loading = true;
      users = await api.getUsers();
    } catch (e) {
      showToast('Error loading user accounts: ' + e.message, 'error');
    } finally {
      loading = false;
    }
  }

  async function handleToggleStatus(u) {
    try {
      await api.toggleUserStatus(u.id);
      showToast(`User status updated successfully`, 'success');
      await loadUsers();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }
</script>

<div class="view-section active">
  {#if loading}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">Loading user accounts...</div>
  {:else if users.length === 0}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">No user accounts registered.</div>
  {:else}
    <div class="card" style="padding: 0;">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Full Name</th>
              <th>Email Address</th>
              <th>Phone Number</th>
              <th>System Role</th>
              <th>Account Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each users as u}
              <tr>
                <td style="font-weight: 600; color: var(--text-primary);">{u.name}</td>
                <td>{u.email}</td>
                <td>{u.phone || '—'}</td>
                <td style="text-transform: capitalize; font-weight: 500;">
                  <span style="display:inline-flex; align-items:center; gap:4px;">
                    <i class="ti {u.role === 'admin' ? 'ti-shield' : u.role === 'manager' ? 'ti-user-shield' : 'ti-user'}"></i>
                    {u.role}
                  </span>
                </td>
                <td>
                  <span class="prop-status {u.status === 'active' ? 'status-occupied' : 'status-maintenance'}">
                    {u.status}
                  </span>
                </td>
                <td>
                  <button 
                    class="topbar-btn" 
                    on:click={() => handleToggleStatus(u)} 
                    style="padding: 4px 8px; font-size: 11px; color: {u.status === 'active' ? 'var(--danger)' : 'var(--success)'}; border-color: {u.status === 'active' ? 'var(--danger-bg)' : 'var(--success-bg)'};"
                  >
                    {u.status === 'active' ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>
