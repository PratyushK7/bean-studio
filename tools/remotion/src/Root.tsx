import {Composition} from 'remotion';
import {NumberCard} from './NumberCard';
import {BillCard} from './BillCard';

export const Root = () => (
  <>
    <Composition id="NumberCard" component={NumberCard} width={1920} height={1080} fps={30} durationInFrames={120}
      defaultProps={{label: 'धनतेरस का बिल', value: 294580, note: '20 ग्राम का एक नेकलेस'}} />
    <Composition id="BillCard" component={BillCard} width={1920} height={1080} fps={30} durationInFrames={150}
      defaultProps={{title: '₹2,94,580 का बिल', total: 294580, rows: [{who: 'गोयल जी: सोना', amt: 260000}, {who: 'सरकार: GST 3%', amt: 8580, red: true}]}} />
  </>
);
