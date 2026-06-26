<script>
  import { onMount } from 'svelte';
  import * as api from '../lib/api.js';
  import { showToast } from '../lib/stores.js';
  import { formatDateMedium, formatCurrency } from '../lib/utils.js';

  export let user = null;

  let agreements = [];
  let bookingRequests = [];
  let properties = [];
  let tenants = [];
  let loading = true;
  let activeTab = 'leases'; // 'leases' or 'bookings'

  // Create Lease Modal variables
  let showLeaseModal = false;
  let selectedPropertyId = '';
  let selectedTenantId = '';
  let leaseStartDate = '';
  let leaseEndDate = '';
  let leaseRent = '';
  let leaseDeposit = '';

  onMount(async () => {
    await refreshData();
  });

  async function refreshData() {
    try {
      loading = true;
      agreements = await api.getAgreements();
      
      if (user.role === 'admin' || user.role === 'manager') {
        bookingRequests = await api.getBookingRequests();
        properties = await api.getProperties({ status: 'vacant' });
        tenants = await api.getTenants();
      }
    } catch (e) {
      showToast('Error loading agreements: ' + e.message, 'error');
    } finally {
      loading = false;
    }
  }

  // Create lease agreement manually
  function openCreateLeaseModal() {
    selectedPropertyId = '';
    selectedTenantId = '';
    leaseStartDate = '';
    leaseEndDate = '';
    leaseRent = '';
    leaseDeposit = '';
    showLeaseModal = true;
  }

  async function handleCreateLeaseSubmit(e) {
    e.preventDefault();
    const payload = {
      property_id: parseInt(selectedPropertyId),
      tenant_id: parseInt(selectedTenantId),
      start_date: leaseStartDate,
      end_date: leaseEndDate,
      rent_amount: leaseRent ? parseInt(leaseRent) : null,
      deposit_amount: leaseDeposit ? parseInt(leaseDeposit) : null
    };

    try {
      await api.createAgreement(payload);
      showToast('Lease agreement registered successfully!', 'success');
      showLeaseModal = false;
      await refreshData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  async function handleTerminateLease(agrId) {
    if (confirm('Are you sure you want to terminate this lease agreement early? The property status will revert to Vacant and future unpaid invoices will be deleted.')) {
      try {
        await api.terminateAgreement(agrId);
        showToast('Lease agreement terminated successfully.', 'success');
        await refreshData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }
  }

  async function handleDeleteAgreement(agrId) {
    if (confirm('Are you sure you want to delete this agreement permanently? All ledger payments associated with it will be deleted!')) {
      try {
        await api.deleteAgreement(agrId);
        showToast('Lease agreement deleted successfully.', 'success');
        await refreshData();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }
  }

  // Booking actions
  async function handleApproveBooking(reqId) {
    if (confirm('Approve this booking request? This will generate a lease agreement and occupy the property.')) {
      try {
        await api.approveBookingRequest(reqId);
        showToast('Booking request approved! Agreement and invoice ledger generated.', 'success');
        await refreshData();
      } catch (e) {
        showToast(e.message, 'error');
      }
    }
  }

  async function handleRejectBooking(reqId) {
    if (confirm('Reject and delete this booking request?')) {
      try {
        await api.deleteBookingRequest(reqId);
        showToast('Booking request rejected.', 'success');
        await refreshData();
      } catch (e) {
        showToast(e.message, 'error');
      }
    }
  }

  $: pendingBookingsCount = bookingRequests.filter(r => r.status === 'pending').length;
</script>

<div class="view-section active">
  <div class="actions-bar">
    <div class="tab-row" style="margin-bottom: 0;">
      <button class="tab {activeTab === 'leases' ? 'active' : ''}" on:click={() => activeTab = 'leases'}>Lease Agreements</button>
      {#if user && (user.role === 'admin' || user.role === 'manager')}
        <button class="tab {activeTab === 'bookings' ? 'active' : ''}" on:click={() => activeTab = 'bookings'}>
          Booking Requests 
          {#if pendingBookingsCount > 0}
            <span class="nav-badge" style="position: static; margin-left: 6px; padding: 1px 6px;">{pendingBookingsCount}</span>
          {/if}
        </button>
      {/if}
    </div>

    {#if activeTab === 'leases' && user && (user.role === 'admin' || user.role === 'manager')}
      <button class="topbar-btn primary" on:click={openCreateLeaseModal}><i class="ti ti-plus"></i> Create Lease</button>
    {/if}
  </div>

  {#if loading}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">Loading...</div>
  {:else}
    {#if activeTab === 'leases'}
      {#if agreements.length === 0}
        <div style="padding:40px; text-align:center; color:var(--text-secondary)">No lease agreements found.</div>
      {:else}
        <div class="card" style="padding: 0;">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Property Details</th>
                  <th>Tenant Signee</th>
                  <th>Lease Duration</th>
                  <th>Rent Fee</th>
                  <th>Outstanding Balance</th>
                  <th>Agreement Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each agreements as a}
                  <tr>
                    <td>
                      <div style="font-weight: 600; color: var(--text-primary);">Property ID: {a.property_id}</div>
                      <!-- In real mode, we might map property objects, here we display basic values -->
                    </td>
                    <td>Tenant ID: {a.tenant_id}</td>
                    <td>
                      <div style="font-size:12px;">{formatDateMedium(a.start_date)}</div>
                      <div style="font-size:11px; color:var(--text-tertiary);">to {formatDateMedium(a.end_date)}</div>
                    </td>
                    <td>{formatCurrency(a.rent_amount)}</td>
                    <td style="font-weight: 600; color: {a.outstanding_balance > 0 ? 'var(--danger)' : 'var(--success)'};">
                      {formatCurrency(a.outstanding_balance)}
                    </td>
                    <td>
                      <span class="prop-status {a.status === 'active' ? 'status-occupied' : 'status-maintenance'}">
                        {a.status}
                      </span>
                    </td>
                    <td>
                      <div style="display: flex; gap: 6px;">
                        {#if a.status === 'active'}
                          <button class="topbar-btn" on:click={() => handleTerminateLease(a.id)} style="padding: 4px 8px; font-size: 11px; color: var(--warning); border-color: var(--warning-bg);">Terminate</button>
                        {/if}
                        <button class="topbar-btn" on:click={() => handleDeleteAgreement(a.id)} style="padding: 4px 8px; font-size: 11px; color: var(--danger); border-color: var(--danger-bg);">Delete</button>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    {:else}
      {#if bookingRequests.length === 0}
        <div style="padding:40px; text-align:center; color:var(--text-secondary)">No booking requests found.</div>
      {:else}
        <div class="card" style="padding: 0;">
          <div class="table-responsive">
            <table class="table">
              <thead>
                <tr>
                  <th>Property ID</th>
                  <th>Tenant ID</th>
                  <th>Requested Term</th>
                  <th>Created Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {#each bookingRequests as req}
                  <tr>
                    <td style="font-weight: 600;">Property #{req.property_id}</td>
                    <td>Tenant #{req.tenant_id}</td>
                    <td>
                      <span style="font-size:12px;">{formatDateMedium(req.start_date)} to {formatDateMedium(req.end_date)}</span>
                    </td>
                    <td>{formatDateMedium(req.created_at)}</td>
                    <td>
                      <span class="prop-status {req.status === 'approved' ? 'status-occupied' : req.status === 'pending' ? 'status-vacant' : 'status-maintenance'}">
                        {req.status}
                      </span>
                    </td>
                    <td>
                      {#if req.status === 'pending'}
                        <div style="display: flex; gap: 6px;">
                          <button class="topbar-btn primary" on:click={() => handleApproveBooking(req.id)} style="padding: 4px 8px; font-size: 11px;">Approve</button>
                          <button class="topbar-btn" on:click={() => handleRejectBooking(req.id)} style="padding: 4px 8px; font-size: 11px; color: var(--danger); border-color: var(--danger-bg);">Reject</button>
                        </div>
                      {:else}
                        <span style="font-size:12px; color:var(--text-tertiary);">No action required</span>
                      {/if}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </div>
      {/if}
    {/if}
  {/if}
</div>

<!-- =========================
     CREATE LEASE MODAL
     ========================= -->
{#if showLeaseModal}
  <div class="modal-overlay active" on:click={() => showLeaseModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2 class="modal-title">Create Lease Agreement</h2>
        <button class="modal-close" on:click={() => showLeaseModal = false}><i class="ti ti-x"></i></button>
      </div>
      <form on:submit={handleCreateLeaseSubmit}>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label" for="leaseProperty">Select Vacant Property</label>
            <select id="leaseProperty" bind:value={selectedPropertyId} class="form-control" required>
              <option value="">-- Select Property --</option>
              {#each properties as p}
                <option value={p.id}>{p.title} (₹{p.rent_amount}/mo)</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label class="form-label" for="leaseTenant">Select Tenant</label>
            <select id="leaseTenant" bind:value={selectedTenantId} class="form-control" required>
              <option value="">-- Select Tenant --</option>
              {#each tenants as t}
                <option value={t.id}>{t.name} ({t.email})</option>
              {/each}
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="startDate">Lease Start Date</label>
              <input type="date" id="startDate" bind:value={leaseStartDate} class="form-control" required>
            </div>
            <div class="form-group">
              <label class="form-label" for="endDate">Lease End Date</label>
              <input type="date" id="endDate" bind:value={leaseEndDate} class="form-control" required>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label" for="leaseRent">Rent Amount (₹) (Optional - Defaults to Property Rent)</label>
              <input type="number" id="leaseRent" bind:value={leaseRent} class="form-control" placeholder="Defaults to property specifications">
            </div>
            <div class="form-group">
              <label class="form-label" for="leaseDeposit">Security Deposit (₹)</label>
              <input type="number" id="leaseDeposit" bind:value={leaseDeposit} class="form-control" placeholder="e.g. 50000">
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="topbar-btn" on:click={() => showLeaseModal = false}>Cancel</button>
          <button type="submit" class="topbar-btn primary">Generate Lease Agreement</button>
        </div>
      </form>
    </div>
  </div>
{/if}
