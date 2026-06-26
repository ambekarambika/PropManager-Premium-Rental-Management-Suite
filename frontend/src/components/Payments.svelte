<script>
  import { onMount } from 'svelte';
  import * as api from '../lib/api.js';
  import { showToast } from '../lib/stores.js';
  import { formatDateMedium, formatCurrency } from '../lib/utils.js';

  export let user = null;

  let payments = [];
  let loading = true;

  // Record Payment Modal variables
  let showRecordModal = false;
  let selectedPaymentId = '';
  let paymentMethod = 'UPI';

  onMount(async () => {
    await loadPayments();
  });

  async function loadPayments() {
    try {
      loading = true;
      payments = await api.getPayments();
    } catch (e) {
      showToast('Error loading ledger: ' + e.message, 'error');
    } finally {
      loading = false;
    }
  }

  function openRecordModal(payId) {
    selectedPaymentId = payId;
    paymentMethod = 'UPI';
    showRecordModal = true;
  }

  async function handleRecordSubmit(e) {
    e.preventDefault();
    try {
      await api.recordPayment(selectedPaymentId, { payment_method: paymentMethod });
      showToast('Payment recorded successfully', 'success');
      showRecordModal = false;
      await loadPayments();
    } catch (err) {
      showToast(err.message, 'error');
    }
  }
</script>

<div class="view-section active">
  {#if loading}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">Loading payments ledger...</div>
  {:else if payments.length === 0}
    <div style="padding:40px; text-align:center; color:var(--text-secondary)">No payment transactions recorded in ledger.</div>
  {:else}
    <div class="card" style="padding: 0;">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr>
              <th>Invoice ID</th>
              <th>Agreement ID</th>
              <th>Rent Amount</th>
              <th>Due Date</th>
              <th>Collection Status</th>
              <th>Settled Date & Method</th>
              {#if user && (user.role === 'admin' || user.role === 'manager')}
                <th>Actions</th>
              {/if}
            </tr>
          </thead>
          <tbody>
            {#each payments as p}
              <tr>
                <td style="font-weight: 600; color: var(--text-primary);">#PAY-{p.id}</td>
                <td>Agreement #{p.agreement_id}</td>
                <td>{formatCurrency(p.amount)}</td>
                <td>{formatDateMedium(p.due_date)}</td>
                <td>
                  <span class="prop-status {p.status === 'paid' ? 'status-occupied' : p.status === 'pending' ? 'status-vacant' : 'status-maintenance'}">
                    {p.status}
                  </span>
                </td>
                <td>
                  {#if p.status === 'paid'}
                    <div style="font-size:12px;">{formatDateMedium(p.payment_date)}</div>
                    <div style="font-size:10px; color:var(--text-tertiary);">via {p.payment_method || 'UPI'}</div>
                  {:else}
                    <span style="font-size:12px; color:var(--text-tertiary);">—</span>
                  {/if}
                </td>
                {#if user && (user.role === 'admin' || user.role === 'manager')}
                  <td>
                    {#if p.status !== 'paid'}
                      <button class="topbar-btn primary" on:click={() => openRecordModal(p.id)} style="padding: 4px 8px; font-size: 11px;">Collect Rent</button>
                    {:else}
                      <span style="font-size:12px; color:var(--text-tertiary);"><i class="ti ti-check"></i> Settled</span>
                    {/if}
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
     RECORD PAYMENT MODAL
     ========================= -->
{#if showRecordModal}
  <div class="modal-overlay active" on:click={() => showRecordModal = false}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2 class="modal-title">Collect Rent Payment</h2>
        <button class="modal-close" on:click={() => showRecordModal = false}><i class="ti ti-x"></i></button>
      </div>
      <form on:submit={handleRecordSubmit}>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label" for="payMethod">Payment Collection Method</label>
            <select id="payMethod" bind:value={paymentMethod} class="form-control" required>
              <option value="UPI">UPI / GPay / PhonePe</option>
              <option value="Net Banking">Net Banking Transfer</option>
              <option value="Card">Credit / Debit Card</option>
              <option value="Cash">Cash Settlement</option>
              <option value="Cheque">Cheque Deposit</option>
            </select>
          </div>
          <div style="font-size:12px; color:var(--text-secondary); line-height:1.5; margin-top:8px;">
            Note: Marking this paid will update the outstanding lease ledger balance instantly.
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="topbar-btn" on:click={() => showRecordModal = false}>Cancel</button>
          <button type="submit" class="topbar-btn primary">Record Payment</button>
        </div>
      </form>
    </div>
  </div>
{/if}
