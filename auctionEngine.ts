import { Player, Team } from '../types/cricket';
import { soundFx } from '../utils/audio';

export interface AuctionState {
  playerPool: Player[];
  currentPlayerIndex: number;
  currentBid: number;
  leadingTeamId: string | null;
  timerSeconds: number;
  isPaused: boolean;
  status: 'active' | 'sold' | 'unsold' | 'completed';
  teams: Team[];
  userTeamId: string;
  auctionLog: string[];
}

export function initializeAuction(playerPool: Player[], teams: Team[], userTeamId: string): AuctionState {
  const firstPlayer = playerPool[0];
  const startingBid = firstPlayer ? firstPlayer.basePrice || 25000 : 25000;

  return {
    playerPool,
    currentPlayerIndex: 0,
    currentBid: startingBid,
    leadingTeamId: null,
    timerSeconds: 8,
    isPaused: false,
    status: 'active',
    teams,
    userTeamId,
    auctionLog: [
      `🔨 Welcome to the Grand Gully Auction! First player under the hammer: ${firstPlayer?.name} (${firstPlayer?.nickname}) - Base Price ₹${startingBid.toLocaleString()}`,
    ],
  };
}

export function placeBid(state: AuctionState, teamId: string, increment: number): AuctionState {
  const team = state.teams.find((t) => t.id === teamId);
  if (!team) return state;

  const newBid = state.currentBid + increment;
  if (team.purse < newBid) {
    return {
      ...state,
      auctionLog: [
        `❌ ${team.name} has insufficient purse (₹${team.purse.toLocaleString()}) to bid ₹${newBid.toLocaleString()}!`,
        ...state.auctionLog,
      ],
    };
  }

  soundFx.playGavel();

  return {
    ...state,
    currentBid: newBid,
    leadingTeamId: teamId,
    timerSeconds: 6, // reset timer on fresh bid
    status: 'active',
    auctionLog: [
      `💰 BID! ${team.name} raises the paddle to ₹${newBid.toLocaleString()}!`,
      ...state.auctionLog,
    ],
  };
}

export function advanceAuctionTick(state: AuctionState): AuctionState {
  if (state.status !== 'active' || state.isPaused) return state;

  const currentPlayer = state.playerPool[state.currentPlayerIndex];
  if (!currentPlayer) {
    return { ...state, status: 'completed' };
  }

  // AI Bidding Logic
  // Occasionally an AI team places a bid if timer > 2
  if (state.timerSeconds > 2 && Math.random() < 0.35) {
    const aiTeams = state.teams.filter((t) => t.id !== state.userTeamId && t.id !== state.leadingTeamId);
    if (aiTeams.length > 0) {
      const bidder = aiTeams[Math.floor(Math.random() * aiTeams.length)];
      const maxBidWilling = (currentPlayer.battingSkill + currentPlayer.bowlingSkill) * 450;
      const nextBid = state.currentBid + 3000;

      if (bidder.purse >= nextBid && nextBid <= maxBidWilling) {
        soundFx.playGavel();
        return {
          ...state,
          currentBid: nextBid,
          leadingTeamId: bidder.id,
          timerSeconds: 6,
          auctionLog: [
            `💰 AI BID! ${bidder.name} bids ₹${nextBid.toLocaleString()} for ${currentPlayer.name}!`,
            ...state.auctionLog,
          ],
        };
      }
    }
  }

  // Decrement timer
  const nextTimer = state.timerSeconds - 1;

  if (nextTimer === 3) {
    return {
      ...state,
      timerSeconds: nextTimer,
      auctionLog: [
        `🔔 Going once for ₹${state.currentBid.toLocaleString()}! Any more bids?`,
        ...state.auctionLog,
      ],
    };
  }

  if (nextTimer === 1) {
    return {
      ...state,
      timerSeconds: nextTimer,
      auctionLog: [
        `🔔 Going twice for ₹${state.currentBid.toLocaleString()}! Last call!`,
        ...state.auctionLog,
      ],
    };
  }

  if (nextTimer <= 0) {
    // Sold or Unsold
    soundFx.playGavel();
    soundFx.playCheer();

    if (state.leadingTeamId) {
      const winningTeam = state.teams.find((t) => t.id === state.leadingTeamId)!;
      const updatedTeams = state.teams.map((t) => {
        if (t.id === state.leadingTeamId) {
          return {
            ...t,
            purse: t.purse - state.currentBid,
            players: [...t.players, currentPlayer],
          };
        }
        return t;
      });

      return {
        ...state,
        status: 'sold',
        timerSeconds: 0,
        teams: updatedTeams,
        auctionLog: [
          `🎉 SOLD! ${currentPlayer.name} is bought by ${winningTeam.name} for ₹${state.currentBid.toLocaleString()}!`,
          ...state.auctionLog,
        ],
      };
    } else {
      return {
        ...state,
        status: 'unsold',
        timerSeconds: 0,
        auctionLog: [
          `❌ UNSOLD! No bids received for ${currentPlayer.name}. Moving to next player.`,
          ...state.auctionLog,
        ],
      };
    }
  }

  return {
    ...state,
    timerSeconds: nextTimer,
  };
}

export function moveToNextPlayer(state: AuctionState): AuctionState {
  const nextIdx = state.currentPlayerIndex + 1;
  if (nextIdx >= state.playerPool.length) {
    return {
      ...state,
      status: 'completed',
      auctionLog: ['🏁 Auction is completed! All players have been presented.', ...state.auctionLog],
    };
  }

  const nextPlayer = state.playerPool[nextIdx];
  const startingBid = nextPlayer.basePrice || 25000;

  return {
    ...state,
    currentPlayerIndex: nextIdx,
    currentBid: startingBid,
    leadingTeamId: null,
    timerSeconds: 7,
    status: 'active',
    auctionLog: [
      `🆕 Next player: ${nextPlayer.name} (${nextPlayer.role}) - Base Price ₹${startingBid.toLocaleString()}`,
      ...state.auctionLog,
    ],
  };
}
