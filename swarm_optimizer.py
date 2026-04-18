"""
Particle Swarm Optimization (PSO) for FD Portfolio Allocation

The Swarm Analogy:
  - Each "particle" represents a possible portfolio allocation across N banks
  - Particles fly through N-dimensional space (one dimension per bank)
  - They're attracted to their own best position AND the swarm's global best
  - Over iterations, the swarm converges on the optimal allocation

Objective Function:
  Maximize: weighted_return - penalty(DICGC_violation) - penalty(concentration_risk)
"""

import random
import math
from typing import List, Dict, Tuple
from copy import deepcopy


class Particle:
    def __init__(self, n_banks: int, total_amount: float):
        self.n_banks = n_banks
        self.total_amount = total_amount

        # Position = allocation weights (fractions summing to 1)
        raw = [random.random() for _ in range(n_banks)]
        total = sum(raw)
        self.position = [r / total for r in raw]

        # Velocity = how fast weights shift
        self.velocity = [random.uniform(-0.1, 0.1) for _ in range(n_banks)]

        self.best_position = self.position.copy()
        self.best_score = float('-inf')
        self.current_score = float('-inf')

    def get_amounts(self) -> List[float]:
        return [w * self.total_amount for w in self.position]


class SwarmOptimizer:
    """
    Particle Swarm Optimizer for Fixed Deposit Portfolio Allocation.
    
    Parameters:
        total_amount: Total investment amount in INR
        risk_profile: 'conservative', 'moderate', or 'aggressive'
        tenure_months: Investment tenure in months
        banks: List of bank data with rates
        dicgc_limit: DICGC insurance limit per bank (default ₹5,00,000)
        num_particles: Swarm size (more = thorough but slower)
        max_iterations: Convergence iterations
    """

    # PSO Hyperparameters
    W = 0.729      # Inertia weight (controls momentum)
    C1 = 1.494     # Cognitive coefficient (pull toward personal best)
    C2 = 1.494     # Social coefficient (pull toward global best)

    # Risk profile: max single-bank concentration
    RISK_LIMITS = {
        "conservative": 0.20,   # Max 20% in any one bank
        "moderate": 0.35,       # Max 35% in any one bank
        "aggressive": 0.50,     # Max 50% in any one bank
    }

    def __init__(self, total_amount: float, risk_profile: str, tenure_months: int,
                 banks: List[Dict], dicgc_limit: float = 500000,
                 num_particles: int = 60, max_iterations: int = 200):
        self.total_amount = total_amount
        self.risk_profile = risk_profile
        self.tenure_months = tenure_months
        self.banks = banks
        self.dicgc_limit = dicgc_limit
        self.num_particles = num_particles
        self.max_iterations = max_iterations
        self.n_banks = len(banks)

        self.particles: List[Particle] = []
        self.global_best_position: List[float] = []
        self.global_best_score = float('-inf')

        # History for visualization
        self.convergence_history: List[float] = []
        self.particle_history: List[List[float]] = []

    def _get_rate(self, bank: Dict) -> float:
        """Get the applicable rate for the given tenure"""
        rates = bank["rates"]
        tenure_str = str(self.tenure_months)
        if tenure_str in rates:
            return rates[tenure_str]
        # Find closest tenure
        available = [int(k) for k in rates.keys()]
        closest = min(available, key=lambda x: abs(x - self.tenure_months))
        return rates[str(closest)]

    def _fitness(self, particle: Particle) -> float:
        """
        Fitness function to MAXIMIZE.
        
        Components:
        1. Expected return (weighted average rate)
        2. DICGC penalty (heavy penalty if any bank exceeds ₹5L)
        3. Concentration penalty (based on risk profile)
        4. Diversification bonus (reward for spreading across banks)
        5. Rating bonus (prefer higher-rated banks)
        """
        amounts = particle.get_amounts()
        weights = particle.position

        # 1. Base return score
        total_return = 0.0
        for i, bank in enumerate(self.banks):
            rate = self._get_rate(bank)
            interest = amounts[i] * (rate / 100) * (self.tenure_months / 12)
            total_return += interest

        normalized_return = total_return / self.total_amount  # as fraction

        # 2. DICGC violation penalty
        dicgc_penalty = 0.0
        for amount in amounts:
            if amount > self.dicgc_limit:
                excess = amount - self.dicgc_limit
                dicgc_penalty += (excess / self.total_amount) * 2.0  # heavy penalty

        # 3. Concentration risk penalty
        max_concentration = self.RISK_LIMITS.get(self.risk_profile, 0.35)
        concentration_penalty = 0.0
        for w in weights:
            if w > max_concentration:
                concentration_penalty += (w - max_concentration) * 1.5

        # 4. Diversification bonus (entropy-based)
        entropy = -sum(w * math.log(w + 1e-10) for w in weights)
        max_entropy = math.log(self.n_banks)
        diversification_bonus = (entropy / max_entropy) * 0.02  # small positive signal

        # 5. Credit rating bonus
        rating_bonus = 0.0
        rating_scores = {"AAA": 0.01, "AA+": 0.008, "AA": 0.006, "A+": 0.004, "A": 0.002}
        for i, bank in enumerate(self.banks):
            rating = bank.get("rating", "A")
            rating_bonus += weights[i] * rating_scores.get(rating, 0.002)

        fitness = (normalized_return
                   - dicgc_penalty
                   - concentration_penalty
                   + diversification_bonus
                   + rating_bonus)

        return fitness

    def _normalize_position(self, position: List[float]) -> List[float]:
        """Ensure weights sum to 1 and are non-negative"""
        clipped = [max(0.001, p) for p in position]
        total = sum(clipped)
        return [c / total for c in clipped]

    def _initialize_swarm(self):
        self.particles = [Particle(self.n_banks, self.total_amount)
                          for _ in range(self.num_particles)]

        # Evaluate initial positions
        for p in self.particles:
            score = self._fitness(p)
            p.current_score = score
            p.best_score = score
            p.best_position = p.position.copy()
            if score > self.global_best_score:
                self.global_best_score = score
                self.global_best_position = p.position.copy()

    def optimize(self) -> Dict:
        """Run PSO and return optimal portfolio allocation"""
        self._initialize_swarm()

        for iteration in range(self.max_iterations):
            # Adaptive inertia: decreases over time for fine-tuning
            w = self.W * (1 - iteration / self.max_iterations * 0.4)

            for particle in self.particles:
                new_velocity = []
                new_position = []

                for d in range(self.n_banks):
                    r1, r2 = random.random(), random.random()

                    # PSO velocity update equation
                    cognitive = self.C1 * r1 * (particle.best_position[d] - particle.position[d])
                    social = self.C2 * r2 * (self.global_best_position[d] - particle.position[d])
                    new_v = w * particle.velocity[d] + cognitive + social

                    # Clamp velocity
                    new_v = max(-0.2, min(0.2, new_v))
                    new_velocity.append(new_v)
                    new_position.append(particle.position[d] + new_v)

                particle.velocity = new_velocity
                particle.position = self._normalize_position(new_position)

                # Evaluate new position
                score = self._fitness(particle)
                particle.current_score = score

                # Update personal best
                if score > particle.best_score:
                    particle.best_score = score
                    particle.best_position = particle.position.copy()

                # Update global best
                if score > self.global_best_score:
                    self.global_best_score = score
                    self.global_best_position = particle.position.copy()

            # Record convergence
            self.convergence_history.append(round(self.global_best_score, 6))

            # Record particle spread (for visualization) - sample 10 particles
            if iteration % 5 == 0:
                sample = [p.position[0] for p in self.particles[:10]]
                self.particle_history.append(sample)

        return self._build_result()

    def _build_result(self) -> Dict:
        """Convert optimal weights into a readable portfolio result"""
        allocation = []
        total_interest = 0.0

        for i, bank in enumerate(self.banks):
            weight = self.global_best_position[i]
            amount = weight * self.total_amount
            rate = self._get_rate(bank)
            interest = amount * (rate / 100) * (self.tenure_months / 12)
            total_interest += interest

            allocation.append({
                "bank_name": bank["name"],
                "bank_id": bank["id"],
                "allocated_amount": round(amount, 2),
                "weight_percent": round(weight * 100, 2),
                "interest_rate": rate,
                "interest_earned": round(interest, 2),
                "maturity_amount": round(amount + interest, 2),
                "dicgc_insured": amount <= self.dicgc_limit,
                "rating": bank.get("rating", "A"),
                "tenure_months": self.tenure_months
            })

        allocation.sort(key=lambda x: x["allocated_amount"], reverse=True)

        annual_return_pct = (total_interest / self.total_amount) * (12 / self.tenure_months) * 100

        return {
            "allocation": allocation,
            "total_investment": self.total_amount,
            "total_interest_earned": round(total_interest, 2),
            "total_maturity_amount": round(self.total_amount + total_interest, 2),
            "expected_annual_return": round(annual_return_pct, 2),
            "tenure_months": self.tenure_months,
            "risk_profile": self.risk_profile,
            "dicgc_compliance": all(a["dicgc_insured"] for a in allocation),
            "num_banks_used": sum(1 for a in allocation if a["weight_percent"] > 2),
            "optimization_score": round(self.global_best_score, 4),
            "iterations_run": self.max_iterations,
            "swarm_size": self.num_particles
        }

    def build_ladder_strategy(self, allocation: List[Dict]) -> List[Dict]:
        """
        Build an FD Ladder Strategy:
        Split each bank allocation into multiple tenures (3, 6, 9, 12 months)
        so that money matures periodically — providing liquidity + reinvestment.
        """
        ladder = []
        tenures = [3, 6, 9, 12]
        splits = [0.20, 0.25, 0.25, 0.30]  # % per rung

        for alloc in allocation[:4]:  # Top 4 banks
            for tenure, split in zip(tenures, splits):
                amount = alloc["allocated_amount"] * split
                rate = self._get_rate(
                    next(b for b in self.banks if b["id"] == alloc["bank_id"])
                ) * (0.95 if tenure < 12 else 1.0)  # slightly lower for shorter tenure
                interest = amount * (rate / 100) * (tenure / 12)
                ladder.append({
                    "bank": alloc["bank_name"],
                    "tenure_months": tenure,
                    "amount": round(amount, 2),
                    "rate": round(rate, 2),
                    "maturity_amount": round(amount + interest, 2),
                    "matures_in": f"{tenure} months"
                })

        return sorted(ladder, key=lambda x: x["tenure_months"])
