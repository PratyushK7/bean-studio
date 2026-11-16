import {AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

// Same tokens as channels/hindi/visual-bible.json graphics: Nirmala UI text, Bahnschrift numbers, warm dark panel, gold.
const inr = (n: number) => '₹' + Math.round(n).toLocaleString('en-IN');

export const NumberCard = ({label, value, note}: {label: string; value: number; note: string}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const enter = spring({frame: f, fps, config: {damping: 200}});
  const count = interpolate(f, [8, 70], [0, value], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const push = interpolate(f, [0, 120], [1, 1.025]);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', transform: `scale(${push})`}}>
      <div style={{opacity: enter, transform: `translateY(${(1 - enter) * 24}px)`, background: 'rgba(23,19,15,0.86)', border: '2px solid #C9A24B',
        borderRadius: 18, padding: '56px 90px', textAlign: 'center'}}>
        <div style={{fontFamily: '"Nirmala UI", sans-serif', fontSize: 56, color: '#E9DFC8'}}>{label}</div>
        <div style={{fontFamily: 'Bahnschrift, sans-serif', fontSize: 168, fontWeight: 700, color: '#E8C36A', lineHeight: 1.1}}>{inr(count)}</div>
        <div style={{fontFamily: '"Nirmala UI", sans-serif', fontSize: 44, color: '#B9AE96'}}>{note}</div>
      </div>
    </AbsoluteFill>
  );
};
