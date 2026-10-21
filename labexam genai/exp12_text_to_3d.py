"""
Experiment 12: Text to 3D Object Generation
Load a pretrained text-to-3D model, provide a textual prompt, and
generate a real 3D mesh (vertices + faces) - rendered from multiple
viewpoints and as a rotating animation, plus exported as a .obj file
you can open and freely rotate in any 3D viewer (Blender, Windows 3D
Viewer, online .obj viewers, etc.).
"""
import torch
from diffusers import ShapEPipeline
from diffusers.utils import export_to_obj
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.animation import FuncAnimation
from IPython.display import Image, display

pipe = ShapEPipeline.from_pretrained("openai/shap-e", torch_dtype=torch.float32)
prompt = input("Enter 3D object prompt (e.g. 'a chair', 'a birthday cupcake'): ")

# output_type="mesh" -> a real 3D mesh (verts/faces), not flat rendered frames
mesh = pipe(prompt, guidance_scale=15.0, num_inference_steps=64, output_type="mesh").images[0]
export_to_obj(mesh, "generated_3d.obj")

verts, faces = mesh.verts.numpy(), mesh.faces.numpy()

def draw(ax, angle):
    ax.clear()
    ax.add_collection3d(Poly3DCollection(verts[faces], facecolor="orange", edgecolor="k", linewidths=0.1))
    ax.set_xlim(verts[:, 0].min(), verts[:, 0].max())
    ax.set_ylim(verts[:, 1].min(), verts[:, 1].max())
    ax.set_zlim(verts[:, 2].min(), verts[:, 2].max())
    ax.view_init(elev=20, azim=angle)
    ax.set_title(f"View: {angle} deg")

# Multiple real 3D viewpoints of the same mesh
fig = plt.figure(figsize=(9, 3))
for i, angle in enumerate([0, 90, 180]):
    draw(fig.add_subplot(1, 3, i + 1, projection="3d"), angle)
plt.tight_layout()
plt.savefig("views.png")
display(Image("views.png"))

# Rotating 3D animation of the same mesh
fig2 = plt.figure()
ax2 = fig2.add_subplot(111, projection="3d")
ani = FuncAnimation(fig2, lambda frame: draw(ax2, frame * 10), frames=36, interval=100)
ani.save("rotation.gif", writer="pillow")
display(Image("rotation.gif"))

print("Saved generated_3d.obj (open in any 3D viewer to rotate freely), views.png, rotation.gif")
