document.addEventListener("DOMContentLoaded", function() {
    const socket = io.connect(window.location.origin);

    document.getElementById("bid-btn").addEventListener("click", async function() {
        const bidAmount = document.getElementById("bid-amount").value;
        const itemId = "{{ item.item_id }}";

        const response = await fetch("/item/bid", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRF-Token": document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ item_id: itemId, bid_amount: bidAmount })
        });

        const data = await response.json();
        if (response.ok) {
            alert("Bid placed successfully!");
        } else {
            alert(data.error);
        }
    });

    socket.on("update_bid", function(data) {
        if (data.item_id === "{{ item.item_id }}") {
            document.getElementById("current-bid").innerText = "£" + data.bid_amount;
        }
    });
});
