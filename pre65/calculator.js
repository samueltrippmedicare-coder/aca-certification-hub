(function (root) {
  'use strict';
  const FPL = {us: [15960, 5680], ak: [19950, 7100], hi: [18360, 6530]};
  const bands = [[100,133,2.15,2.15],[133,150,3.23,4.30],[150,200,4.30,6.78],[200,250,6.78,8.66],[250,300,8.66,10.22],[300,401,10.22,10.22]];
  function contributionRate(pct) {
    if (pct < 100 || pct > 400) return null;
    const b = bands.find(b => pct >= b[0] && pct < b[1]);
    return (b[2] + (b[3] - b[2]) * (pct - b[0]) / (b[1] - b[0])) / 100;
  }
  function calculate(d) {
    const g = FPL[d.region] || FPL.us;
    const fpl = g[0] + g[1] * (d.hh - 1);
    const gross = d.wages + d.se + d.trad + d.roth + d.ss + d.pen + d.inv + d.other;
    const magi = Math.max(0, gross - d.hsa - d.ded), pct = magi / fpl * 100;
    const rate = contributionRate(pct), cliff = 4 * fpl;
    const hsaUnconfirmed = d.hsa > 0 && (d.hsaRoom === null || d.hsa > d.hsaRoom);
    const enrollment = d.enroll === null ? d.bench : d.enroll;
    const credit = rate !== null && pct >= 138 && d.bench > 0 && !hsaUnconfirmed
      ? Math.min(enrollment, Math.max(0, d.bench - magi * rate / 12)) * d.months : null;
    return {magi, pct, cliff, headroom: cliff-magi, rate, credit, hsaUnconfirmed};
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {calculate, contributionRate};
  if (!root.document) return;
  const $ = id => document.getElementById(id);
  const money = n => n.toLocaleString('en-US', {style:'currency',currency:'USD',maximumFractionDigits:2});
  const keys = ['wages','se','trad','roth','ss','pen','inv','other','hsa','ded','bench','enroll','months'];
  function render() {
    const inputs = Array.from($('calc').querySelectorAll('input'));
    const invalid = inputs.find(el => !el.validity.valid || (el.value && !Number.isFinite(Number(el.value))));
    if (invalid || !$('i-months').value) {
      $('r-verdict').className = 'verdict bad';
      $('r-verdict').textContent = 'Check your entries. Eligible months must be a whole number from 1 to 12; deductions and premiums cannot be negative.';
      ['r-magi','r-fpl','r-cliff','r-rate'].forEach(id => $(id).textContent = '—');
      return;
    }
    const d = {hh:Number($('hh').value),region:$('region').value};
    keys.forEach(k => {d[k] = Number($('i-'+k).value || 0);});
    d.enroll = $('i-enroll').value === '' ? null : d.enroll;
    d.hsaRoom = $('i-hsa-room').value === '' ? null : Number($('i-hsa-room').value);
    const r = calculate(d);
    $('r-magi').textContent = money(r.magi);
    $('r-fpl').textContent = (Math.round(r.pct*100)/100).toFixed(2)+'%';
    $('r-cliff').textContent = money(r.cliff);
    $('r-rate').textContent = r.rate === null ? 'Outside income range' : (r.rate*100).toFixed(2)+'%';
    $('r-pin').style.left = Math.min(100,r.pct/5)+'%';
    let cls = 'ok', msg = '';
    if (r.pct < 100) {
      cls = 'low'; msg = '<strong>Below the usual Marketplace income floor.</strong> Generally no federal premium tax credit at this projected income. Check Medicaid, other coverage and any applicable exception. Annual income alone does not determine Medicaid eligibility.';
    } else if (r.pct < 138) {
      cls = 'low'; msg = '<strong>Confirm Medicaid and Marketplace eligibility.</strong> In an expansion state, current monthly income may qualify the household for Medicaid. In a non-expansion state, Marketplace assistance may be available if otherwise eligible. No credit estimate is shown until eligibility is resolved; a one-time income event does not resolve every month.';
    } else if (r.pct <= 400) {
      cls = r.headroom < 5000 ? 'warn' : 'ok';
      msg = '<strong>'+ (r.headroom === 0 ? 'Exactly at the 400% FPL limit.' : 'At or below the cliff, with '+money(r.headroom)+' of headroom.') + '</strong> ';
      if (r.pct <= 250) msg += 'If otherwise eligible, consider Silver cost-sharing reductions. ';
      if (r.credit !== null) msg += 'Illustrative credit for '+d.months+' eligible month'+(d.months===1?'':'s')+': <strong>'+money(r.credit)+'</strong>. ';
      if (r.headroom < 5000) msg += 'Leave a buffer for unexpected taxable income; eligibility is not guaranteed by this income result.';
      else msg += 'Coordinate planned withdrawals and conversions with the tax professional and retain an income buffer.';
    } else {
      cls = 'bad'; msg = '<strong>Above the cliff by '+money(-r.headroom)+'.</strong> No federal premium tax credit at this projected income. Reaching 400% FPL would require '+money(-r.headroom)+' less MAGI. Review only allowable deductions and changes to future income; completed Roth conversions cannot be recharacterized. HSA deductions require eligibility and unused allowable room.';
    }
    if (r.hsaUnconfirmed) {
      cls = 'warn'; msg = '<strong>HSA deduction needs confirmation.</strong> The displayed MAGI is provisional and no credit estimate is shown. Enter the confirmed personal deduction allowance after eligibility, proration and employer contributions; the claimed deduction cannot exceed that amount. '+msg;
    }
    $('r-verdict').className = 'verdict '+cls;
    $('r-verdict').innerHTML = msg;
  }
  $('calc').addEventListener('submit', e => e.preventDefault());
  $('calc').addEventListener('input', render);
  $('calc').addEventListener('change', render);
  render();
  const links = Array.from(document.querySelectorAll('.rail nav a'));
  if ('IntersectionObserver' in root) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries.find(e => e.isIntersecting);
      if (visible) links.forEach(a => {
        const active = a.hash === '#'+visible.target.id;
        a.classList.toggle('active',active);
        if(active) a.setAttribute('aria-current','location'); else a.removeAttribute('aria-current');
      });
    },{rootMargin:'-10% 0px -65% 0px'});
    document.querySelectorAll('section.guide').forEach(s => observer.observe(s));
  }
})(typeof window !== 'undefined' ? window : globalThis);
