from yg.projects.models import Projects, Project

def test_priority_earlier():
    """
    When searching projects, an earlier match must always precede a later
    one, regardless of length.
    """
    ps = Projects([
        Project(name='anon project but longer', id='a'),
        Project(name='simple project', id='b'),
    ])
    psr = Projects(reversed(ps))

    # a should always be selected because the search appears earlier
    assert ps.best('project').id == 'a'
    assert psr.best('project').id == 'a'
