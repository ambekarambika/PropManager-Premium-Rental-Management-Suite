<script>
  import { onMount } from 'svelte';
  import * as api from '../lib/api.js';
  import { showToast } from '../lib/stores.js';
  import { formatDateMedium } from '../lib/utils.js';

  export let user = null;

  let tickets = [];
  let properties = []; // vacant/occupied owned by user
  let loading = true;
  let activeTab = 'active'; // 'active' or 'resolved'

  // Report issue modal variables
  let showReportModal = false;
  let selectedPropertyId = '';
  let issueDesc = '';
  let urgencyLevel = 'pending';
  let issueNotes = '';

  // Update Notes modal variables
  let showUpdateModal = false;
  let selectedTicketId = '';
  let ticketStatus = 'pending';
  let ticketNotes = '';

  onMount(async () => {
    await refreshData();
  });

  async function refreshData() {
    try {
      loading = true;
      tickets = await api.getMaintenanceTickets();
      properties = await api.getProperties();
    } catch (e) {
      showToast('Error loading tickets: ' + e.message, 'error');
    } finally {
      loading = false;
    }
  }

  function openReportModal() {
    selectedPropertyId = '';
    issueDesc = '';
    urgencyLevel = 'pending';
    issueNotes = '';
    showReportModal = true;
  }

  async function handleReportSubmit(e) {
    e.preventDefault();
    const payload = {
      property_id: parseInt(selectedPropertyId),
      description: issueDesc,
      status: urgencyLevel,
      notes: issueNotes || 'Reported by user.'
    };

    try {
      await api.createMaintenanceTicket(payload);
      showToast('Maintenance issue reported successfully!', 'success');
      showReportModal = false;
      await refreshData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  function openUpdateModal(ticket) {
    selectedTicketId = ticket.id;
    ticketStatus = ticket.status;
    ticketNotes = ticket.notes || '';
    showUpdateModal = true;
  }

  async function handleUpdateSubmit(e) {
    e.preventDefault();
    try {
      await api.updateMaintenanceTicket(selectedTicketId, {
        status: ticketStatus,
        notes: ticketNotes
      });
      showToast('Maintenance ticket updated successfully', 'success');
      showUpdateModal = false;
      await refreshData();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }

  $: filteredTickets = tickets.filter(t => {
    if (activeTab === 'active') {
      return t.status !== 'done';
    } else {
      return t.status === 'done';
    }
  });
</script>

<div class="view-section active">
  <div class="actions-bar" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
    <div class="tab-row" style="margin-bottom: 0;">
      <button class="tab {activeTab === 'active' ? 'active' : ''}" on:click={() => activeTab = 'active'}>Active Tickets</button>
      <button class="tab {activeTab === 'resolved' ? 'active' : ''}" on:click={() => activeTab = 'resolved'}>Resolved Tickets</button>
    </div>
    
    {#if user && user.role === 'tenant'}
      <button class="topbar-btn primary" on:click={openReportModal}><i class="ti ti-plus"></i> Report Issue</button>
    {/if}
  </div>

  {#if loading}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">Loading maintenance log...</div>
  {:else if filteredTickets.length === 0}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">No maintenance tickets in this section.</div>
  {:else}
    <div class="card" style="padding: 0;">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Property ID</th>
              <th>Issue Description</th>
              <th>Reported Date</th>
              <th>Urgency Level</th>
              <th>Resolution Notes / Updates</th>
              {#if user && (user.role === 'admin' || user.role === 'manager')}
                <th>Actions</th>
              {/if}
            </tr>
          </thead>
          <tbody>
            {#each filteredTickets as t}
              <tr>
                <td style="font-weight: 600; color: var(--text-primary);">Property #{t.property_id}</td>
                <td>{t.description}</td>
                <td>{formatDateMedium(t.reported_date)}</td>
                <td>
                  <span class="maint-badge badge-{t.status}">{t.status}</span>
                </td>
                <td>{t.notes || '—'}</td>
                {#if user && (user.role === 'admin' || user.role === 'manager')}
                  <td>
                    <button class="topbar-btn" on:click={() => openUpdateModal(t)} style="padding: 4px 8px; font-size: 11px;"><i class="ti ti-edit"></i> Manage</button>
                  </td>
                {/if}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

<!-- =========================
     REPORT ISSUE MODAL
     ========================= -->
{#if showReportModal}
  <div class="modal-overlay active" on:click={() => showReportModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2 class="modal-title">Report Maintenance Issue</h2>
        <button class="modal-close" on:click={() => showReportModal = false}><i class="ti ti-x"></i></button>
      </div>
      <form on:submit={handleReportSubmit}>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label" for="reportProp">Select Property Unit</label>
            <select id="reportProp" bind:value={selectedPropertyId} class="form-control" required>
              <option value="">-- Select Property --</option>
              {#each properties as p}
                <option value={p.id}>{p.title}</option>
              {/each}
            </select>
          </div>

          <div class="form-group">
            <label class="form-label" for="reportDesc">Describe the Issue</label>
            <textarea id="reportDesc" bind:value={issueDesc} class="form-control" rows="3" placeholder="e.g. Master bedroom shower is leaking water continuously..." required></textarea>
          </div>

          <div class="form-group">
            <label class="form-label" for="reportUrgency">Urgency Level</label>
            <select id="reportUrgency" bind:value={urgencyLevel} class="form-control" required>
              <option value="pending">Standard (Pending)</option>
              <option value="urgent">Urgent Resolution Required</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label" for="reportNotes">Additional Details (Optional)</label>
            <input type="text" id="reportNotes" bind:value={issueNotes} class="form-control" placeholder="e.g. Electrician suggested visits after 4 PM.">
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="topbar-btn" on:click={() => showReportModal = false}>Cancel</button>
          <button type="submit" class="topbar-btn primary">Submit Issue Ticket</button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- =========================
     UPDATE STATUS / RESOLVE TICKET MODAL
     ========================= -->
{#if showUpdateModal}
  <div class="modal-overlay active" on:click={() => showUpdateModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2 class="modal-title">Manage Maintenance Ticket</h2>
        <button class="modal-close" on:click={() => showUpdateModal = false}><i class="ti ti-x"></i></button>
      </div>
      <form on:submit={handleUpdateSubmit}>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label" for="updateStatus">Update Urgency / Completion Status</label>
            <select id="updateStatus" bind:value={ticketStatus} class="form-control" required>
              <option value="pending">Pending</option>
              <option value="urgent">Urgent</option>
              <option value="done">Resolved (Done)</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label" for="updateNotes">Resolution Notes / Comments</label>
            <textarea id="updateNotes" bind:value={ticketNotes} class="form-control" rows="3" placeholder="Explain plumbing visits, electrical fixes, dates, etc." required></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="topbar-btn" on:click={() => showUpdateModal = false}>Cancel</button>
          <button type="submit" class="topbar-btn primary">Save Updates</button>
        </div>
      </form>
    </div>
  </div>
{/if}
