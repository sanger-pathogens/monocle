from hypothesis import strategies as st
from hypothesis.extra.django import from_model

from juno.api.models import Sample, Institution, User, Affiliation

# models
users = from_model(User)
institutions = from_model(Institution)
samples = from_model(Sample, submitting_institution=institutions)
affiliations = from_model(Affiliation, institution=institutions, user=users)


@st.composite
def db(
    draw,
    min_users=0,
    max_users=5,
    min_institutions=0,
    max_institutions=5,
    min_samples=0,
    max_samples=30,
):
    # draw independent tables
    drawn_users = draw(
        st.lists(
            users,
            min_size=min_users,
            max_size=max_users,
            unique_by=(lambda user: user.email,),
        )
    )
    drawn_institutions = draw(
        st.lists(
            institutions,
            min_size=min_institutions,
            max_size=max_institutions,
            unique_by=(lambda institution: institution.name,),
        )
    )

    # helper booleans
    can_draw_affiliation = len(drawn_institutions) > 0 and len(drawn_users) > 0
    can_draw_sample = len(drawn_institutions) > 0

    # draw dependent tables (with foreign keys)
    drawn_affiliations = (
        draw(
            st.lists(
                from_model(
                    Affiliation,
                    user=st.sampled_from(drawn_users),
                    institution=st.sampled_from(drawn_institutions),
                ),
                min_size=min_users * min_institutions
                if can_draw_affiliation
                else 0,
                max_size=max_users * max_institutions
                if can_draw_affiliation
                else 0,
            )
        )
        if can_draw_affiliation
        else []
    )
    drawn_samples = (
        draw(
            st.lists(
                from_model(
                    Sample,
                    submitting_institution=st.sampled_from(drawn_institutions),
                ),
                min_size=min_samples if can_draw_sample else 0,
                max_size=max_samples if can_draw_sample else 0,
                unique_by=(
                    lambda sample: sample.lane_id,
                    lambda sample: sample.sample_id,
                    lambda sample: sample.public_name,
                ),
            )
        )
        if can_draw_sample
        else []
    )

    # return state
    return {
        "users": drawn_users,
        "institutions": drawn_institutions,
        "affiliations": drawn_affiliations,
        "samples": drawn_samples,
    }
