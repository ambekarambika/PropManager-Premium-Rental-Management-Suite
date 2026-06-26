<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import * as api from '../lib/api.js';
  import { currentView, showToast } from '../lib/stores.js';
  import { formatDateShort, formatDateMedium, formatCurrency } from '../lib/utils.js';

  export let user = null;

  const dispatch = createEventDispatcher();

  let loading = true;
  let data = null;
  let properties = []; // for unassigned tenant explorer or manager properties
  let bookingRequests = []; // for unassigned tenant requests
  let activeFilter = 'all';

  // Svelte state for leased property gallery thumbnail switcher
  let activeThumbIdx = 0;

  onMount(async () => {
    await refreshDashboard();
  });

  async function refreshDashboard() {
    try {
      loading = true;
      data = await api.getDashboardData(user.role);
      
      if (user.role === 'tenant' && !data.lease) {
        // Load vacant properties for booking requests
        properties = await api.getProperties({ status: 'vacant' });
        bookingRequests = await api.getBookingRequests();
      } else if (user.role === 'admin' || user.role === 'manager') {
        properties = await api.getProperties();
      }
    } catch (e) {
      showToast('Error loading dashboard: ' + e.message, 'error');
    } finally {
      loading = false;
    }
  }

  function handleSwitchView(viewName) {
    currentView.set(viewName);
  }

  $: filteredProperties = properties.filter(p => {
    if (activeFilter === 'all') return true;
    return p.status === activeFilter;
  });

  async function handleCancelLease(leaseId) {
    if (confirm('Are you sure you want to cancel your lease agreement early? The property status will shift to Vacant.')) {
      try {
        await api.terminateAgreement(leaseId);
        showToast('Your lease has been cancelled successfully.', 'success');
        await refreshDashboard();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }
  }

  async function handleCancelBookingRequest(reqId) {
    if (confirm('Are you sure you want to cancel this booking request?')) {
      try {
        await api.deleteBookingRequest(reqId);
        showToast('Booking request cancelled.', 'success');
        await refreshDashboard();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }
  }

  function handleViewDetails(propertyId) {
    dispatch('view-details', { propertyId });
  }

  $: getLeaseImages = () => {
    if (!data || !data.lease) return [];
    const imgs = [data.lease.image_url];
    if (data.lease.interior_images) {
      data.lease.interior_images.split(',').forEach(url => {
        if (url.trim()) imgs.push(url.trim());
      });
    }
    return imgs;
  };
</script>

{#if loading}
  <div style="padding: 40px; text-align: center; color: var(--text-secondary);">Loading dashboard data...</div>
{:else if data}
  {#if user.role === 'admin' || user.role === 'manager'}
    <!-- KPI Row -->
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-label"><i class="ti ti-building-estate"></i> Total properties</div>
        <div class="kpi-value">{data.kpi.totalProperties}</div>
        <div class="kpi-sub kpi-neutral"><i class="ti ti-chart-bar"></i> Registered in portfolio</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label"><i class="ti ti-home-check"></i> Occupancy</div>
        <div class="kpi-value">{data.kpi.occupancyRate}</div>
        <div class="kpi-sub kpi-up"><i class="ti ti-circle-check"></i> Active tenancies</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label"><i class="ti ti-cash"></i> Rent this month</div>
        <div class="kpi-value">{data.kpi.rentCollected}</div>
        <div class="kpi-sub kpi-neutral"><i class="ti ti-clock"></i> <span>{data.kpi.pendingRent}</span> pending</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-label"><i class="ti ti-tool"></i> Open tickets</div>
        <div class="kpi-value">{data.kpi.openTickets}</div>
        <div class="kpi-sub kpi-down"><i class="ti ti-alert-triangle"></i> <span>{data.kpi.urgentTickets} urgent</span></div>
      </div>
    </div>

    <!-- Content Sections -->
    <div class="two-col">
      <div>
        <div class="card" style="padding: 20px;">
          <div class="section-header" style="margin-bottom: 12px;">
            <div class="section-title">Property Portfolio Status</div>
            <button class="topbar-btn" on:click={() => handleSwitchView('properties')} style="font-size: 11px; padding: 4px 10px;">View All</button>
          </div>
          
          <div style="display: flex; gap: 10px; margin-bottom: 15px;">
            <button class="tab {activeFilter === 'all' ? 'active' : ''}" on:click={() => activeFilter = 'all'}>All</button>
            <button class="tab {activeFilter === 'occupied' ? 'active' : ''}" on:click={() => activeFilter = 'occupied'}>Occupied</button>
            <button class="tab {activeFilter === 'vacant' ? 'active' : ''}" on:click={() => activeFilter = 'vacant'}>Vacant</button>
          </div>

          <div class="list-wrapper" style="max-height: 290px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px;">
            {#if filteredProperties.length === 0}
              <div style="font-size: 12px; color: var(--text-secondary); text-align: center; padding: 20px 0;">
                No properties in this category.
              </div>
            {:else}
              {#each filteredProperties as p}
                <div class="prop-card" on:click={() => handleViewDetails(p.id)} style="cursor: pointer;">
                  <div class="prop-thumb {p.type}"><i class="ti ti-home"></i></div>
                  <div class="prop-info">
                    <div class="prop-name" style="font-size: 13px; font-weight: 700;">{p.title}</div>
                    <div class="prop-loc" style="font-size: 11px;"><i class="ti ti-map-pin"></i> {p.address}, {p.city}</div>
                  </div>
                  <div class="prop-meta">
                    <div class="prop-rent" style="font-size: 13px; font-weight: 700;">{formatCurrency(p.rent_amount)}</div>
                    <span class="prop-status status-{p.status}">{p.status}</span>
                  </div>
                </div>
              {/each}
            {/if}
          </div>
        </div>
      </div>

      <div class="right-panel">
        <!-- Rent due card -->
        <div class="mini-card">
          <div class="section-header" style="margin-bottom: 12px;">
            <div class="section-title">Rent Due Soon</div>
            <span class="section-link" on:click={() => handleSwitchView('payments')}>Ledger <i class="ti ti-chevron-right"></i></span>
          </div>
          <div class="due-rents-list">
            {#if data.dueRents.length === 0}
              <div style="font-size: 12px; color: var(--text-secondary); padding: 10px 0; text-align: center;">No pending payments</div>
            {:else}
              {#each data.dueRents as item}
                <div class="rent-item">
                  <span class="rent-dot {item.status === 'overdue' ? 'dot-red' : 'dot-amber'}"></span>
                  <span class="rent-tenant">{item.tenantName}</span>
                  <span class="rent-days">{item.status === 'overdue' ? 'Overdue' : 'Due'} {formatDateShort(item.dueDate)}</span>
                  <span class="rent-amount">{item.amount}</span>
                </div>
              {/each}
            {/if}
          </div>
        </div>

        <!-- Maintenance card -->
        <div class="mini-card">
          <div class="section-header" style="margin-bottom: 12px;">
            <div class="section-title">Maintenance Tickets</div>
            <span class="section-link" on:click={() => handleSwitchView('maintenance')}>Open requests <i class="ti ti-chevron-right"></i></span>
          </div>
          <div style="font-size: 12px; color: var(--text-secondary); text-align: center; padding: 10px 0;">
            Check status of open plumbing, electrical, and facility issues in the Maintenance panel.
          </div>
        </div>
      </div>
    </div>

    <div class="bottom-row">
      <!-- Collection trend chart -->
      <div class="card">
        <div class="section-header">
          <div class="section-title">Rent Collection Trend</div>
          <span style="font-size: 11px; color: var(--text-secondary);">Last 6 Months (Dynamic)</span>
        </div>
        <div class="bar-chart" style="display: flex; align-items: flex-end; justify-content: space-around; height: 120px; border-bottom: 1px solid var(--border-primary); margin-top: 15px;">
          {#each data.collectionTrend as height, i}
            <div class="bar-col" style="display: flex; flex-direction: column; align-items: center; width: 40px;">
              <div style="background: var(--primary); height: {height}px; width: 100%; border-radius: 4px 4px 0 0; transition: height 0.3s ease;"></div>
              <span class="bar-lbl" style="font-size: 10px; margin-top: 4px;">{data.collectionTrendLabels ? data.collectionTrendLabels[i] : ''}</span>
            </div>
          {/each}
        </div>
      </div>

      <!-- Activity logs -->
      <div class="card">
        <div class="section-header">
          <div class="section-title">System Activity Log</div>
        </div>
        <div style="display: flex; flex-direction: column; gap: 8px;">
          {#each data.recentActivity as act}
            <div class="act-item" style="display: flex; align-items: flex-start; gap: 10px; padding: 4px 0;">
              <div class="act-dot" style="background: var(--primary); width: 6px; height: 6px; border-radius: 50%; margin-top: 6px;"></div>
              <div>
                <div class="act-text" style="font-size: 12.5px; color: var(--text-secondary);">{@html act.text}</div>
                <div class="act-time" style="font-size: 10px; color: var(--text-tertiary);">{act.time}</div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    </div>

  {:else if user.role === 'tenant'}
    {#if data.lease}
      <!-- Active Tenant Dashboard -->
      <div class="two-col">
        <!-- Lease Terms -->
        <div class="card">
          <div class="section-header">
            <div class="section-title">My Lease Terms & Agreement</div>
          </div>
          
          <!-- Image switcher gallery -->
          <div class="prop-gallery-container" style="margin-bottom: 15px;">
            <img src={getLeaseImages()[activeThumbIdx]} class="prop-gallery-main" alt="Leased Property" style="width: 100%; height: 200px; border-radius: var(--radius-md); object-fit: cover;">
            {#if getLeaseImages().length > 1}
              <div class="prop-gallery-thumbs" style="display: flex; gap: 8px; margin-top: 8px; overflow-x: auto;">
                {#each getLeaseImages() as img, idx}
                  <img 
                    src={img} 
                    alt="thumb" 
                    class="prop-gallery-thumb {activeThumbIdx === idx ? 'active' : ''}" 
                    on:click={() => activeThumbIdx = idx}
                    style="width: 50px; height: 38px; border-radius: 4px; object-fit: cover; cursor: pointer; border: 2px solid {activeThumbIdx === idx ? 'var(--primary)' : 'transparent'}; opacity: {activeThumbIdx === idx ? 1 : 0.6};"
                  >
                {/each}
              </div>
            {/if}
          </div>

          <div style="font-size: 16px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;">{data.lease.propertyName}</div>
          <div style="font-size: 13px; color: var(--text-secondary); display: flex; align-items: center; gap: 4px; margin-bottom: 16px;">
            <i class="ti ti-map-pin"></i> {data.lease.address}
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; background: var(--bg-secondary); padding: 14px; border-radius: var(--radius-md); margin-bottom: 14px;">
            <div>
              <div style="font-size: 11px; color: var(--text-tertiary); text-transform: uppercase; font-weight: 600;">Monthly Rent</div>
              <div style="font-size: 16px; font-weight: 700; color: var(--text-primary); margin-top: 2px;">{data.lease.rent}</div>
            </div>
            <div>
              <div style="font-size: 11px; color: var(--text-tertiary); text-transform: uppercase; font-weight: 600;">Security Deposit</div>
              <div style="font-size: 16px; font-weight: 700; color: var(--text-primary); margin-top: 2px;">{data.lease.deposit}</div>
            </div>
          </div>

          <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary); margin-bottom: 14px;">
            <span>Start: <strong>{formatDateMedium(data.lease.startDate)}</strong></span>
            <span>End: <strong>{formatDateMedium(data.lease.endDate)}</strong></span>
          </div>

          <!-- Owner Contacts Info -->
          <div style="border-top: 1px solid var(--border-tertiary); padding-top: 12px; margin-bottom: 14px;">
            <div style="font-size: 11px; color: var(--text-tertiary); text-transform: uppercase; font-weight: 700; margin-bottom: 8px;">My Property Contacts</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
              <div style="padding: 8px; background: var(--bg-secondary); border-radius: var(--radius-sm); border-left: 2px solid var(--primary); min-width: 0;">
                <div style="font-size: 9px; color: var(--text-tertiary); font-weight: 600;">MANAGER</div>
                <div style="font-size: 11px; font-weight: 700; color: var(--text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{data.contacts.manager.name}</div>
                <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;"><i class="ti ti-phone" style="font-size: 9px;"></i> {data.contacts.manager.phone}</div>
              </div>
              <div style="padding: 8px; background: var(--bg-secondary); border-radius: var(--radius-sm); border-left: 2px solid #185FA5; min-width: 0;">
                <div style="font-size: 9px; color: var(--text-tertiary); font-weight: 600;">OWNER</div>
                <div style="font-size: 11px; font-weight: 700; color: var(--text-primary); text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{data.lease.owner_name || 'Owner'}</div>
                <div style="font-size: 10px; color: var(--text-secondary); margin-top: 2px;"><i class="ti ti-phone" style="font-size: 9px;"></i> {data.lease.owner_phone || 'None'}</div>
              </div>
            </div>
          </div>

          <div style="border-top: 1px solid var(--border-tertiary); padding-top: 12px; display: flex; justify-content: flex-end;">
            <button class="topbar-btn btn-cancel-lease" on:click={() => handleCancelLease(data.lease.id)} style="color:var(--danger); border-color:var(--danger-bg); font-size:12px; padding:6px 12px; display:inline-flex; align-items:center; gap:4px; cursor:pointer;">
              <i class="ti ti-ban"></i> Cancel Lease Contract
            </button>
          </div>
        </div>

        <div class="right-panel">
          <!-- Next Payment Due widget -->
          <div class="mini-card" style="background: var(--bg-primary); border-top: 4px solid var(--primary);">
            {#if data.nextPayment}
              <div style="font-size:11px;color:var(--text-secondary);font-weight:600;text-transform:uppercase">Next Rent Payment Due</div>
              <div style="font-size:24px;font-weight:700;color:var(--text-primary);margin:4px 0">{data.nextPayment.amount}</div>
              <div style="display:flex;align-items:center;justify-content:space-between;margin-top:12px">
                <span style="font-size:12px;color:var(--text-secondary)">Due Date: <strong>{formatDateMedium(data.nextPayment.dueDate)}</strong></span>
                <span class="prop-status {data.nextPayment.status === 'overdue' ? 'status-maintenance' : 'status-vacant'}">{data.nextPayment.status}</span>
              </div>
            {:else}
              <div style="font-size:11px;color:var(--text-secondary);font-weight:600;text-transform:uppercase">Next Rent Payment Due</div>
              <div style="font-size:16px;font-weight:600;color:var(--success);margin-top:8px">All rent payments up to date!</div>
            {/if}
          </div>

          <!-- Contacts card -->
          <div class="mini-card">
            <div class="section-header">
              <div class="section-title">Support Desk</div>
            </div>
            <div style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.5;">
              Have plumbing, wall paint, electrical, or other repair issues? Switch to <strong style="color: var(--primary); cursor: pointer;" on:click={() => handleSwitchView('maintenance')}>Maintenance log</strong> to report a new ticket.
            </div>
          </div>
        </div>
      </div>

      <!-- Payments history table -->
      <div class="card">
        <div class="section-header">
          <div class="section-title">Lease Rent Payments Ledger</div>
        </div>
        <div class="table-responsive">
          <table class="table">
            <thead>
              <tr>
                <th>Rent Period Due Date</th>
                <th>Amount Due</th>
                <th>Payment Status</th>
                <th>Settled Date</th>
              </tr>
            </thead>
            <tbody>
              {#if data.payments.length === 0}
                <tr><td colspan="4" style="text-align:center;color:var(--text-secondary)">No payment records found</td></tr>
              {:else}
                {#each data.payments as p}
                  <tr>
                    <td>{formatDateMedium(p.due_date)}</td>
                    <td>{formatCurrency(p.amount)}</td>
                    <td>
                      <span class="prop-status {p.status === 'paid' ? 'status-occupied' : p.status === 'pending' ? 'status-vacant' : 'status-maintenance'}">
                        {p.status}
                      </span>
                    </td>
                    <td>{p.payment_date ? formatDateMedium(p.payment_date) : '—'}</td>
                  </tr>
                {/each}
              {/if}
            </tbody>
          </table>
        </div>
      </div>

    {:else}
      <!-- Unassigned Tenant Dashboard -->
      <div class="two-col">
        <!-- Available Properties Explorer -->
        <div class="card">
          <div class="section-header">
            <div class="section-title">Available Vacant Properties to Book</div>
          </div>
          
          <div class="list-wrapper">
            {#if properties.length === 0}
              <div style="text-align:center;padding:20px;color:var(--text-secondary)">No vacant properties currently available. Check back later!</div>
            {:else}
              {#each properties as p}
                <div class="prop-card" on:click={() => handleViewDetails(p.id)}>
                  <div class="prop-thumb {p.type}"><i class="ti ti-home"></i></div>
                  <div class="prop-info">
                    <div class="prop-name">{p.title}</div>
                    <div class="prop-loc"><i class="ti ti-map-pin"></i> {p.address}, {p.city}</div>
                  </div>
                  <div class="prop-meta">
                    <div class="prop-rent">{formatCurrency(p.rent_amount)}/mo</div>
                    <span class="prop-status status-vacant">vacant</span>
                  </div>
                </div>
              {/each}
            {/if}
          </div>
        </div>

        <!-- My Booking Requests -->
        <div class="right-panel">
          <div class="mini-card">
            <div class="section-header" style="margin-bottom:12px">
              <div class="section-title">My Booking Requests</div>
            </div>
            
            <div style="display:flex; flex-direction:column; gap:10px;">
              {#if bookingRequests.length === 0}
                <div style="font-size:12px;color:var(--text-secondary);text-align:center;padding:10px 0;">No active requests</div>
              {:else}
                {#each bookingRequests as req}
                  <div style="padding:10px; background:var(--bg-secondary); border-radius:var(--radius-md); border-left:3px solid var(--primary); display:flex; flex-direction:column; gap:6px;">
                    <div style="font-size:12px; font-weight:700; color:var(--text-primary); text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">
                      {req.property_title || `Property ID: ${req.property_id}`}
                    </div>
                    <div style="font-size:11px; color:var(--text-secondary); display:flex; justify-content:space-between;">
                      <span>Requested: {formatDateShort(req.created_at)}</span>
                      <span class="prop-status {req.status === 'approved' ? 'status-occupied' : req.status === 'pending' ? 'status-vacant' : 'status-maintenance'}">
                        {req.status}
                      </span>
                    </div>
                    {#if req.status === 'pending'}
                      <button on:click={() => handleCancelBookingRequest(req.id)} style="font-size:10px; color:var(--danger); border:none; background:none; text-align:right; cursor:pointer; font-weight:600; padding: 2px 0;">
                        Cancel Request
                      </button>
                    {/if}
                  </div>
                {/each}
              {/if}
            </div>
          </div>
        </div>
      </div>
    {/if}
  {/if}
{/if}
