import React from 'react';

export const AlertPanel = ({ alerts = [], onApprove, onDispatch }) => (
  <section className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm" aria-label="Alert review queue">
    <div className="mb-3 flex items-center justify-between">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500">Alert review queue</h3>
      <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-700">
        {alerts.filter(item => item.status === 'pending_review').length} pending
      </span>
    </div>
    <div className="max-h-52 space-y-2 overflow-y-auto">
      {alerts.length === 0 && <p className="text-xs text-gray-400">No alerts require action.</p>}
      {alerts.map(alert => (
        <article key={alert.id} className="rounded-xl border border-gray-100 bg-gray-50 p-3 text-xs">
          <div className="flex justify-between gap-2">
            <strong className="uppercase text-primary">{alert.payload?.severity || 'alert'} · {alert.channel}</strong>
            <span className="text-gray-500">{alert.status}</span>
          </div>
          <p className="mt-1 text-gray-600">{alert.payload?.evidence?.[0]}</p>
          <div className="mt-2 flex gap-2">
            {alert.status === 'pending_review' && alert.channel !== 'dashboard' && (
              <button onClick={() => onApprove(alert.id)} className="rounded-lg bg-secondary px-2 py-1 font-semibold text-white">Approve</button>
            )}
            {(alert.status === 'approved' || alert.status === 'failed') && (
              <button onClick={() => onDispatch(alert.id)} className="rounded-lg bg-primary px-2 py-1 font-semibold text-white">Dispatch</button>
            )}
          </div>
        </article>
      ))}
    </div>
  </section>
);
