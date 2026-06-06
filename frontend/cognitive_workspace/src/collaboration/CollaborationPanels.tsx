export function MultiOperatorCognitionMap({ operators }: { operators: string[] }) {
  return (
    <div className="multi-operator-cognition-map">
      {operators.map((operator) => (
        <span key={operator} className="operator-node">{operator}</span>
      ))}
    </div>
  );
}

export function SharedMissionDag({ missions }: { missions: string[] }) {
  return (
    <ol className="shared-mission-dag">
      {missions.map((mission) => (
        <li key={mission}>{mission}</li>
      ))}
    </ol>
  );
}

export function OperatorConstellation({ active }: { active: number }) {
  return <div className="operator-constellation" data-active={active} />;
}

export function DelegationFlowGraph({ chains }: { chains: string[] }) {
  return (
    <div className="delegation-flow-graph">
      {chains.map((chain) => (
        <span key={chain} className="delegation-chain">{chain}</span>
      ))}
    </div>
  );
}

export function TeamPressureRadar({ pressure }: { pressure: number }) {
  return <div className="team-pressure-radar" data-pressure={pressure} />;
}

export function CollaborativeReplayTimeline({ events }: { events: string[] }) {
  return (
    <ol className="collaborative-replay-timeline">
      {events.map((event) => (
        <li key={event}>{event}</li>
      ))}
    </ol>
  );
}

export function SupervisionAuthorityOverlay({ authority }: { authority: string }) {
  return <div className="supervision-authority-overlay" data-authority={authority} />;
}

export function CollaborativeCognitionPulse({ pulse }: { pulse: string }) {
  return <div className="collaborative-cognition-pulse" data-pulse={pulse} />;
}
