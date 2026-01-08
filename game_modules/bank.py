import streamlit as st
from datetime import datetime

def _inject_bank_styles():
    """Keep the same 'Town Hub' look so the Bank feels like part of Gold Creek."""
    st.markdown(
        """
        <style>
            .content-box{
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 18px;
                padding: 22px 22px 10px 22px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.18);
                margin-bottom: 14px;
            }
            .town-subtitle{
                margin-top:-8px;
                opacity:0.85;
                font-style: italic;
            }
            .town-card{
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 16px;
                padding: 16px 16px 10px 16px;
                height: 100%;
            }
            .town-card h3{
                margin: 0 0 6px 0;
            }
            .town-card p{
                margin: 0 0 10px 0;
                opacity: 0.9;
            }
            .small-note{
                opacity: 0.8;
                font-size: 0.9rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def _init_bank_state():
    st.session_state.setdefault("bank_balance", 0)
    st.session_state.setdefault("bank_ledger", [])

def _log(action: str, amount: int, note: str = ""):
    st.session_state.bank_ledger.insert(
        0,
        {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "amount": int(amount),
            "bank_balance": int(st.session_state.bank_balance),
            "wallet_gold": int(st.session_state.gold),
            "note": note,
        },
    )

def render_bank():
    """Gold Creek Bank — same look as Town Hub, with a frontier sense of humor."""
    _inject_bank_styles()
    _init_bank_state()

    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    st.markdown("# 🏦 **GOLD CREEK BANK**")
    st.markdown('<div class="town-subtitle">Where your gold is *probably* safer than under your mattress… probably.</div>', unsafe_allow_html=True)

    # Headline balances
    colA, colB, colC = st.columns([1,1,1])
    with colA:
        st.metric("💼 Wallet Gold", f"{st.session_state.gold:,}")
    with colB:
        st.metric("🔒 Bank Vault", f"{st.session_state.bank_balance:,}")
    with colC:
        st.metric("📈 Daily Interest*", "0.5%", help="*Interest subject to change based on: moon phase, sheriff mood, and whether the teller likes your hat.")

    st.divider()

    col1, col2, col3 = st.columns(3, gap="large")

    # --- Deposit / Withdraw ---
    with col1:
        st.markdown('<div class="town-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Teller Window")
        st.markdown("Deposit or withdraw like a civilized outlaw.")

        max_deposit = int(max(0, st.session_state.gold))
        deposit_amt = st.number_input("Deposit amount", min_value=0, max_value=max_deposit, value=min(10, max_deposit), step=1)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("➕ Deposit", use_container_width=True, disabled=(deposit_amt <= 0)):
                if deposit_amt <= st.session_state.gold:
                    st.session_state.gold -= int(deposit_amt)
                    st.session_state.bank_balance += int(deposit_amt)
                    _log("Deposit", int(deposit_amt), "Teller nodded politely.")
                    st.success(f"Deposited {int(deposit_amt):,} gold.")
                else:
                    st.error("Insufficient gold!")
        with c2:
            max_withdraw = int(max(0, st.session_state.bank_balance))
            if st.button("➖ Withdraw", use_container_width=True, disabled=(max_withdraw <= 0)):
                amt = int(min(deposit_amt, max_withdraw)) if deposit_amt > 0 else min(10, max_withdraw)
                st.session_state.bank_balance -= int(amt)
                st.session_state.gold += int(amt)
                _log("Withdraw", int(amt), "Teller squinted suspiciously.")
                st.success(f"Withdrew {int(amt):,} gold.")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Loans / Credit ---
    with col2:
        st.markdown('<div class="town-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Loan Desk")
        st.markdown("Need capital? We offer loans with reasonable terms.")

        # Handle reputation - check if it's a dict (faction system) or number
        reputation_data = st.session_state.get("reputation", {})
        if isinstance(reputation_data, dict) and reputation_data:
            # Calculate average faction reputation
            rep_values = [v for v in reputation_data.values() if isinstance(v, (int, float))]
            rep = int(sum(rep_values) / len(rep_values)) if rep_values else 50
        else:
            # Default reputation
            rep = 50

        st.progress(min(1.0, max(0.0, rep/100)))
        st.caption(f"Reputation Score: {rep}/100")

        loan_amt = st.slider("Loan amount", 0, 500, 100, 10)
        
        if st.button("📎 Apply for Loan", use_container_width=True, disabled=(loan_amt <= 0)):
            collateral = st.session_state.bank_balance
            score = rep + min(40, collateral/25)
            threshold = 35 + (loan_amt/12)
            
            if score >= threshold:
                st.session_state.gold += int(loan_amt)
                _log("Loan Approved", int(loan_amt), "Loan approved")
                st.success(f"Approved! {loan_amt:,} gold added to wallet.")
            else:
                st.warning("Loan denied. Improve reputation or add collateral.")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Services ---
    with col3:
        st.markdown('<div class="town-card">', unsafe_allow_html=True)
        st.markdown("### 🔒 Bank Services")
        
        st.checkbox("🛡️ Robbery Insurance", help="Covers theft and mishaps")
        st.checkbox("🎩 VIP Recognition", value=True, help="Premium service")
        
        st.markdown("#### 📰 Bank News")
        st.markdown("- New vault security installed")
        st.markdown("- Interest rates stable")
        st.markdown("- Gold storage capacity increased")

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # --- Ledger ---
    st.markdown("### 📚 Transaction Ledger")
    if st.session_state.bank_ledger:
        st.dataframe(st.session_state.bank_ledger, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet.")

    st.markdown("</div>", unsafe_allow_html=True)