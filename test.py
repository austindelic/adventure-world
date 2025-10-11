import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(4, 4))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

# Sky (top half)
ax.fill_between([0, 1], 0.5, 1, color="skyblue")

# Ground (bottom half)
ax.fill_between([0, 1], 0, 0.5, color="green")

ax.set_axis_off()
plt.show()
