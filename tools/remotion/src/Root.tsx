import {Composition} from 'remotion';
import {NumberCard} from './NumberCard';

export const Root = () => (
  <Composition id="NumberCard" component={NumberCard} width={1920} height={1080} fps={30} durationInFrames={120}
    defaultProps={{label: 'ज्वेलर की अपनी कमाई', value: 294580, note: 'हर तीन लाख के बिल में'}} />
);
