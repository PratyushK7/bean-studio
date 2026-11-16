import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

const inr = (n: number) => '₹' + Math.round(n).toLocaleString('en-IN');
const T = {gold: '#E8C36A', text: '#EFE6D2', dim: '#B9AE96', loss: '#E0715F', panel: 'rgba(20,16,12,0.80)'};
const HI = '"Nirmala UI", sans-serif', NUM = 'Bahnschrift, sans-serif';

export const BillCard = ({title, rows, total}: {title: string; rows: {who: string; amt: number; red?: boolean}[]; total: number}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const enter = spring({frame: f, fps, config: {damping: 200}});
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <div style={{width: 1040, background: T.panel, borderRadius: 22, padding: '48px 64px', opacity: enter, transform: `translateY(${(1 - enter) * 30}px)`,
        boxShadow: '0 30px 80px rgba(0,0,0,0.5), inset 0 0 0 1.5px rgba(232,195,106,0.45)'}}>
        <div style={{fontFamily: HI, fontSize: 54, color: T.text, marginBottom: 28}}>{title}</div>
        {rows.map((r, i) => {
          const a = spring({frame: f - 14 - i * 12, fps, config: {damping: 18, stiffness: 140}});
          return (
            <div key={i} style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', padding: '14px 0', borderTop: '1px solid rgba(232,195,106,0.18)',
              opacity: a, transform: `translateX(${(1 - a) * 60}px)`}}>
              <span style={{fontFamily: HI, fontSize: 46, color: T.text}}>{`${i + 1}. ${r.who}`}</span>
              <span style={{fontFamily: NUM, fontSize: 54, fontWeight: 700, color: r.red ? T.loss : T.gold}}>{inr(r.amt)}</span>
            </div>
          );
        })}
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', paddingTop: 22, marginTop: 8, borderTop: '3px solid ' + T.gold,
          opacity: interpolate(f, [14 + rows.length * 12, 26 + rows.length * 12], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}}>
          <span style={{fontFamily: HI, fontSize: 50, color: T.text}}>कुल</span>
          <span style={{fontFamily: NUM, fontSize: 78, fontWeight: 700, color: T.gold, textShadow: '0 0 28px rgba(232,195,106,0.4)'}}>{inr(total)}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
