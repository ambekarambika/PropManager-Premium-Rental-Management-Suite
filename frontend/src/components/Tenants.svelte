<script>
  import { onMount } from 'svelte';
  import * as api from '../lib/api.js';
  import { showToast } from '../lib/stores.js';

  export let user = null;

  let tenants = [];
  let loading = true;

  // Modal onboard variables
  let showOnboardModal = false;
  let tenantId = '';
  let editMode = false;
  let tenantName = '';
  let tenantEmail = '';
  let tenantPhone = '';
  let tenantEmergency = '';

  onMount(async () => {
    await loadTenants();
  });

  async function loadTenants() {
    try {
      loading = true;
      tenants = await api.getTenants();
    } catch (e) {
      showToast('Error loading tenants: ' + e.message, 'error');
    } finally {
      loading = false;
    }
  }

  function openOnboardModal() {
    editMode = false;
    tenantId = '';
    tenantName = '';
    tenantEmail = '';
    tenantPhone = '';
    tenantEmergency = '';
    showOnboardModal = true;
  }

  function openEditModal(t) {
    editMode = true;
    tenantId = t.id;
    tenantName = t.name;
    tenantEmail = t.email;
    tenantPhone = t.phone || '';
    tenantEmergency = t.emergency_contact || '';
    showOnboardModal = true;
  }

  async function handleOnboardSubmit(e) {
    e.preventDefault();
    const payload = {
      name: tenantName,
      email: tenantEmail,
      phone: tenantPhone,
      emergency_contact: tenantEmergency
    };

    try {
      if (editMode) {
        await api.updateTenant(tenantId, payload);
        showToast('Tenant profile updated successfully', 'success');
      } else {
        await api.createTenant(payload);
        showToast('New tenant profile onboarded. Default password is "tenant123".', 'success');
      }
      showOnboardModal = false;
      await loadTenants();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function handleDeleteTenant(t) {
    if (confirm(`Are you sure you want to delete tenant "${t.name}"? This will terminate their active leases, delete payments, and remove their user account!`)) {
      try {
        await api.deleteTenant(t.id);
        showToast('Tenant profile and linked user account deleted successfully', 'success');
        await loadTenants();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }
  }
</script>

<div class="view-section active">
  <div class="actions-bar">
    <div></div>
    <button class="topbar-btn primary" on:click={openOnboardModal}><i class="ti ti-plus"></i> Onboard Tenant</button>
  </div>

  {#if loading}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">Loading tenant records...</div>
  {:else if tenants.length === 0}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">No tenant records found.</div>
  {:else}
    <div class="card" style="padding: 0;">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Tenant Name</th>
              <th>Email Address</th>
              <th>Phone Number</th>
              <th>Emergency Contact</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each tenants as t}
              <tr>
                <td style="font-weight: 600; color: var(--text-primary);">{t.name}</td>
                <td>{t.email}</td>
                <td>{t.phone || '—'}</td>
                <td>{t.emergency_contact || '—'}</td>
                <td>
                  <div style="display: flex; gap: 8px;">
                    {#if !user || user.role !== 'manager'}
                      <button class="topbar-btn" on:click={() => openEditModal(t)} style="padding: 4px 8px; font-size: 11px;"><i class="ti ti-edit"></i> Edit</button>
                    {/if}
                    <button class="topbar-btn" on:click={() => handleDeleteTenant(t)} style="padding: 4px 8px; font-size: 11px; color: var(--danger); border-color: var(--danger-bg);"><i class="ti ti-trash"></i> Delete</button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

<!-- =========================
     ONBOARD TENANT MODAL
     ========================= -->
{#if showOnboardModal}
  <div class="modal-overlay active" on:click={() => showOnboardModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2 class="modal-title">{editMode ? 'Edit Tenant Profile' : 'Onboard New Tenant'}</h2>
        <button class="modal-close" on:click={() => showOnboardModal = false}><i class="ti ti-x"></i></button>
      </div>
      <form on:submit={handleOnboardSubmit}>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label" for="tenantName">Tenant Full Name</label>
            <input type="text" id="tenantName" bind:value={tenantName} class="form-control" placeholder="e.g. Arjun Sharma" required>
          </div>
          <div class="form-group">
            <label class="form-label" for="tenantEmail">Email Address</label>
            <input type="email" id="tenantEmail" bind:value={tenantEmail} class="form-control" placeholder="arjun@example.com" required readonly={editMode}>
          </div>
          <div class="form-group">
            <label class="form-label" for="tenantPhone">Phone Number</label>
            <input type="text" id="tenantPhone" bind:value={tenantPhone} class="form-control" placeholder="e.g. +91 98765 11111" required>
          </div>
          <div class="form-group">
            <label class="form-label" for="tenantEmergency">Emergency Contact Details</label>
            <input type="text" id="tenantEmergency" bind:value={tenantEmergency} class="form-control" placeholder="e.g. Amit Sharma: +91 98765 99991">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="topbar-btn" on:click={() => showOnboardModal = false}>Cancel</button>
          <button type="submit" class="topbar-btn primary">{editMode ? 'Save Profile' : 'Onboard Tenant'}</button>
        </div>
      </form>
    </div>
  </div>
{/if}
