from math import pi
import pytest
import numpy as np

from firedrake import *
# Must come after firedrake import (that loads MPI)
try:
    import gmshpy
except ImportError:
    gmshpy = None


def integrate_one(m):
    V = FunctionSpace(m, 'CG', 1)
    u = Function(V)
    u.interpolate(Expression("1"))
    return assemble(u * dx)


def test_unit_interval():
    assert abs(integrate_one(UnitIntervalMesh(3)) - 1) < 1e-3


def test_interval():
    assert abs(integrate_one(IntervalMesh(3, 5.0)) - 5.0) < 1e-3


def test_interval_three_arg():
    assert abs(integrate_one(IntervalMesh(10, -1, 1)) - 2.0) < 1e-3


def test_interval_negative_length():
    with pytest.raises(RuntimeError):
        IntervalMesh(10, 2, 1)


def test_periodic_unit_interval():
    assert abs(integrate_one(PeriodicUnitIntervalMesh(3)) - 1) < 1e-3


def test_periodic_interval():
    assert abs(integrate_one(PeriodicIntervalMesh(3, 5.0)) - 5.0) < 1e-3


def test_unit_square():
    assert abs(integrate_one(UnitSquareMesh(3, 3)) - 1) < 1e-3


def test_rectangle():
    assert abs(integrate_one(RectangleMesh(3, 3, 10, 2)) - 20) < 1e-3


def test_unit_cube():
    assert abs(integrate_one(UnitCubeMesh(3, 3, 3)) - 1) < 1e-3


def test_one_element_mesh():
    mesh = PeriodicRectangleMesh(10, 1, Lx=1.0, Ly=1.0)
    V = FunctionSpace(mesh, "CG", 1)
    Vdg = FunctionSpace(mesh, "DG", 1)
    r = Function(Vdg)
    u = Function(V)

    # Checking that if interpolate a double periodic function
    # to DG then projecting to CG returns the same function
    r.interpolate(Expression("sin(2*pi*x[0])"))
    u.project(r)
    assert(abs(assemble((u-r)*(u-r)*dx)) < 1.0e-4)

    # Checking that if interpolate an x-periodic function
    # to DG then projecting to CG does not return the same function
    r.interpolate(Expression("x[1]"))
    u.project(r)
    assert(abs(assemble((u-0.5)*(u-0.5)*dx)) < 1.0e-4)

    # Checking that if interpolate an x-periodic function
    # to DG then projecting to CG does not return the same function
    r.interpolate(Expression("x[0]"))
    u.project(r)
    assert(abs(assemble((u-r)*(u-r)*dx)) > 1.0e-2)


def test_box():
    assert abs(integrate_one(BoxMesh(3, 3, 3, 1, 2, 3)) - 6) < 1e-3


def test_unit_circle():
    pytest.importorskip('gmshpy')
    assert abs(integrate_one(UnitCircleMesh(4)) - pi * 0.5 ** 2) < 0.02


def test_unit_triangle():
    assert abs(integrate_one(UnitTriangleMesh()) - 0.5) < 1e-3


def test_unit_tetrahedron():
    assert abs(integrate_one(UnitTetrahedronMesh()) - 0.5 / 3) < 1e-3


@pytest.mark.parallel
def test_unit_interval_parallel():
    assert abs(integrate_one(UnitIntervalMesh(30)) - 1) < 1e-3


@pytest.mark.parallel
def test_interval_parallel():
    assert abs(integrate_one(IntervalMesh(30, 5.0)) - 5.0) < 1e-3


@pytest.mark.parallel
def test_periodic_unit_interval_parallel():
    assert abs(integrate_one(PeriodicUnitIntervalMesh(30)) - 1) < 1e-3


@pytest.mark.parallel
def test_periodic_interval_parallel():
    assert abs(integrate_one(PeriodicIntervalMesh(30, 5.0)) - 5.0) < 1e-3


@pytest.mark.parallel
def test_unit_square_parallel():
    assert abs(integrate_one(UnitSquareMesh(5, 5)) - 1) < 1e-3


@pytest.mark.parallel
def test_unit_cube_parallel():
    assert abs(integrate_one(UnitCubeMesh(3, 3, 3)) - 1) < 1e-3


@pytest.mark.skipif("gmshpy is None", reason='gmshpy not available')
@pytest.mark.parallel
def test_unit_circle_parallel():
    assert abs(integrate_one(UnitCircleMesh(4)) - pi * 0.5 ** 2) < 0.02


def assert_num_exterior_facets_equals_zero(m):
    # Need to initialise the mesh so that exterior facets have been
    # built.
    m.init()
    assert m.exterior_facets.set.total_size == 0


def run_icosahedral_sphere_mesh_num_exterior_facets():
    m = UnitIcosahedralSphereMesh(0)
    assert_num_exterior_facets_equals_zero(m)


def test_icosahedral_sphere_mesh_num_exterior_facets():
    run_icosahedral_sphere_mesh_num_exterior_facets()


@pytest.mark.parallel(nprocs=2)
def test_icosahedral_sphere_mesh_num_exterior_facets_parallel():
    run_icosahedral_sphere_mesh_num_exterior_facets()


def run_cubed_sphere_mesh_num_exterior_facets():
    m = UnitCubedSphereMesh(0)
    assert_num_exterior_facets_equals_zero(m)


def test_cubed_sphere_mesh_num_exterior_facets():
    run_cubed_sphere_mesh_num_exterior_facets()


@pytest.mark.parallel(nprocs=2)
def test_cubed_sphere_mesh_num_exterior_facets_parallel():
    run_cubed_sphere_mesh_num_exterior_facets()


@pytest.fixture(params=range(1, 4))
def degree(request):
    return request.param


def run_bendy_icos(degree):
    m = IcosahedralSphereMesh(5.0, refinement_level=1, degree=degree)
    coords = m.coordinates.dat.data
    assert np.allclose(np.linalg.norm(coords, axis=1), 5.0)


def run_bendy_icos_unit(degree):
    m = UnitIcosahedralSphereMesh(refinement_level=1, degree=degree)
    coords = m.coordinates.dat.data
    assert np.allclose(np.linalg.norm(coords, axis=1), 1.0)


def test_bendy_icos(degree):
    return run_bendy_icos(degree)


def test_bendy_icos_unit(degree):
    return run_bendy_icos_unit(degree)


@pytest.mark.parallel(nprocs=2)
def test_bendy_icos_parallel(degree):
    return run_bendy_icos(degree)


@pytest.mark.parallel(nprocs=2)
def test_bendy_icos_unit_parallel(degree):
    return run_bendy_icos_unit(degree)


def run_bendy_cube(degree):
    m = CubedSphereMesh(5.0, refinement_level=1, degree=degree)
    coords = m.coordinates.dat.data
    assert np.allclose(np.linalg.norm(coords, axis=1), 5.0)


def run_bendy_cube_unit(degree):
    m = UnitCubedSphereMesh(refinement_level=1, degree=degree)
    coords = m.coordinates.dat.data
    assert np.allclose(np.linalg.norm(coords, axis=1), 1.0)


def test_bendy_cube(degree):
    return run_bendy_cube(degree)


def test_bendy_cube_unit(degree):
    return run_bendy_cube_unit(degree)


@pytest.mark.parallel(nprocs=2)
def test_bendy_cube_parallel(degree):
    return run_bendy_cube(degree)


@pytest.mark.parallel(nprocs=2)
def test_bendy_cube_unit_parallel(degree):
    return run_bendy_cube_unit(degree)


def test_mesh_reordering_defaults_on():
    assert parameters["reorder_meshes"]
    m = UnitSquareMesh(1, 1)
    m.init()

    assert m._did_reordering


def run_mesh_validation():
    from os.path import abspath, dirname, join
    meshfile = join(abspath(dirname(__file__)), "..", "meshes",
                    "broken_rogue_point.msh")
    with pytest.raises(ValueError):
        # Reading a mesh with points not reachable from cell closures
        # should raise ValueError
        Mesh(meshfile)


def test_mesh_validation():
    run_mesh_validation()


@pytest.mark.parallel(nprocs=2)
def test_mesh_validation_parallel():
    run_mesh_validation()


@pytest.mark.parametrize("reorder",
                         [False, True])
def test_force_reordering_works(reorder):
    m = UnitSquareMesh(1, 1, reorder=reorder)
    m.init()

    assert m._did_reordering == reorder


@pytest.mark.parametrize("reorder",
                         [False, True])
def test_changing_default_reorder_works(reorder):
    old_reorder = parameters["reorder_meshes"]
    try:
        parameters["reorder_meshes"] = reorder
        m = UnitSquareMesh(1, 1)
        m.init()

        assert m._did_reordering == reorder
    finally:
        parameters["reorder_meshes"] = old_reorder


if __name__ == '__main__':
    import os
    pytest.main(os.path.abspath(__file__))
