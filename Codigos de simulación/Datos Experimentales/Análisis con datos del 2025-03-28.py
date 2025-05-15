import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d, UnivariateSpline

# Datos originales
dx = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17, 18, 20,
               22, 23, 25, 27, 28, 30, 32, 33, 35, 37, 38, 40, 42, 43, 45, 47,
               48, 50, 52, 53, 55, 57, 58, 60, 61, 62, 63, 64, 65])
dy = np.array([0.6, 0.8, 1.4, 2.8, 3.4, 3.8, 4.6, 5.1, 5.8, 6.2, 6.5, 7.0, 7.4,
               7.7, 8.2, 9.3, 9.9, 10.3, 10.7, 10.9, 11.2, 11.7, 12.0, 12.2, 12.8,
               13.0, 13.5, 13.9, 13.9, 14.4, 15.0, 15.1, 15.3, 15.6, 15.6, 15.7,
               16.3, 16.5, 16.7, 16.9, 17.0, 17.3, 17.4, 17.5, 17.8, 18.2, 18.6])

# Interpolación para completar los valores faltantes
interp_func = interp1d(dx, dy, kind='cubic', fill_value="extrapolate")

# Crear una curva más suave
dx_full = np.linspace(0, 65, 300)
dy_smooth = interp_func(dx_full)

# Ajuste con un spline para suavizar
spline = UnivariateSpline(dx_full, dy_smooth, s=1)
dy_spline = spline(dx_full)

# Definir modelo de ajuste para la parte externa (cono suavizado)
def smooth_cone_model(r, A, B, C, D):
    return A * np.sqrt(r + B) + C + D * r**2

params_smooth_cone, _ = curve_fit(smooth_cone_model, dx, dy, p0=[-5, 1, 10, 0.0005])
dy_smooth_cone = smooth_cone_model(dx_full, *params_smooth_cone)

# Inicializar la curva final copiando la spline
dy_final = dy_spline.copy()

# Modificar los primeros puntos (0 a 4 cm) para aplicar la esfera y blending
def sphere_profile(r, R=3, h_min=1.2):
    return h_min + (R - np.sqrt(R**2 - r**2))

# Regiones de interés
pure_sphere_region = dx_full <= 1.5
blend_region = (dx_full > 1.5) & (dx_full < 4)
cone_region = dx_full >= 1.5

# Perfil de la esfera
dy_sphere = sphere_profile(dx_full)

# Asignar esfera pura en la parte interna (0 a 2 cm)
dy_final[pure_sphere_region] = dy_sphere[pure_sphere_region]

# Blending suave entre 2 y 4 cm
alpha_blend = (dx_full[blend_region] - 1.5) / (4 - 1.5)
dy_final[blend_region] = (1 - alpha_blend) * dy_sphere[blend_region] + alpha_blend * dy_smooth_cone[blend_region]

# Asignar el cono suavizado a partir de 4 cm
dy_final[cone_region] = dy_smooth_cone[cone_region]

# Graficar la versión final corregida
plt.figure(figsize=(8,6))
plt.plot(dx, dy, 'ro', label='Datos originales')
plt.plot(dx_full, dy_final, 'c-', linewidth=2, label='Perfil final suavizado con blending visible')
plt.xlabel("Distancia desde el centro (cm)")
plt.ylabel("Altura de la tela (cm)")
plt.title("Perfil final corregido con blending suave entre esfera y cono (visible entre 2 y 4 cm)")
plt.legend()
plt.grid()
plt.show()

# =========================
# 🔥 Ahora generamos los puntos corregidos cada 0.5 cm
# =========================

dx_points = np.arange(0, 65.1, 0.1)  # desde 0 hasta 65 cada 0.5 cm

# Interpolamos los valores Y sobre la curva corregida final
from scipy.interpolate import interp1d
curve_interpolator = interp1d(dx_full, dy_final, kind='linear')
dy_points = curve_interpolator(dx_points)

# Imprimir la lista completa de puntos corregidos
corrected_points = list(zip(dx_points, dy_points))
print("\n📋 Lista de puntos corregidos cada 0.5 cm:\n")
for point in corrected_points:
    print(f"x = {point[0]:.1f} cm, y = {point[1]:.2f} cm")
