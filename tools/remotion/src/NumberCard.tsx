import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

const inr = (n: number) => '₹' + Math.round(n).toLocaleString('en-IN');
const HI = '"Nirmala UI", sans-serif', NUM = 'Bahnschrift, sans-serif';

export const NumberCard = ({label, value, note}: {label: string; value: number; note: string}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const enter = spring({frame: f, fps, config: {damping: 200}});
  const count = interpolate(f, [6, 62], [0, value], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: (t) => 1 - Math.pow(1 - t, 3)});
  const push = interpolate(f, [0, 120], [1, 1.025]);
  const rule = interpolate(f, [30, 66], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', transform: `scale(${push})`}}>
      <div style={{textAlign: 'center', opacity: enter, transform: `translateY(${(1 - enter) * 24}px)`}}>
        <div style={{fontFamily: HI, fontSize: 60, color: '#EFE6D2', textShadow: '0 4px 24px rgba(0,0,0,0.6)'}}>{label}</div>
        <div style={{fontFamily: NUM, fontSize: 230, fontWeight: 700, color: '#E8C36A', lineHeight: 1.05,
          textShadow: '0 0 60px rgba(232,195,106,0.35), 0 6px 30px rgba(0,0,0,0.6)'}}>{inr(count)}</div>
        <div style={{height: 4, width: 560 * rule, background: '#E8C36A', margin: '6px auto 22px', borderRadius: 2}} />
        <div style={{fontFamily: HI, fontSize: 48, color: '#B9AE96', textShadow: '0 3px 18px rgba(0,0,0,0.6)'}}>{note}</div>
      </div>
    </AbsoluteFill>
  );
};
